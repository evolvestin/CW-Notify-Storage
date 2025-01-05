from decimal import Decimal
from datetime import datetime
from database.session import Session
from sqlalchemy import func, select, literal
from sqlalchemy.engine.row import Row as SQLAlchemyRow
from database.models import Lots, AllTimeStats, PeriodStats


class StatsQueries:
    @staticmethod
    def statistics_query(item_id: str, quality: str = None, stamp: int = None) -> select:
        """Запрос для выборки всех лотов по item_id и фильтрация по статусу"""
        sold_query = select(
            Lots.price
        ).filter(
            Lots.item_id == literal(item_id),
            Lots.status.notin_(['#active', 'Cancelled']),  # Игнорируем активные и отмененные
            Lots.buyer_castle.isnot(None),  # Проверяем, что покупатель есть
        )

        unsold_query = select(
            func.count().label('unsold_count')
        ).filter(
            Lots.item_id == literal(item_id),
            Lots.buyer_castle.is_(None),  # Покупателя нет
            Lots.status.notin_(['#active', 'Cancelled'])  # Статус не Cancelled
        )

        cancelled_query = select(
            func.count().label('cancelled_count')
        ).filter(
            Lots.item_id == literal(item_id),
            Lots.status == literal('Cancelled')  # Статус Cancelled
        )

        if quality is not None:
            if quality == 'Common':
                quality_condition = Lots.quality.is_(None)
            else:
                quality_condition = (Lots.quality == literal(quality))

            sold_query = sold_query.filter(quality_condition)
            unsold_query = unsold_query.filter(quality_condition)
            cancelled_query = cancelled_query.filter(quality_condition)

        if stamp is not None:
            sold_query = sold_query.order_by(Lots.stamp.desc())  # Дополнительная сортировка
            sold_query = sold_query.filter(Lots.stamp >= stamp)
            unsold_query = unsold_query.filter(Lots.stamp >= stamp)
            cancelled_query = cancelled_query.filter(Lots.stamp >= stamp)

        sold_cte = sold_query.cte('sold_cte')
        unsold_cte = unsold_query.cte('unsold_cte')
        cancelled_cte = cancelled_query.cte('cancelled_cte')

        median_query = select(
            func.percentile_cont(0.5).within_group(sold_cte.c.price).label('median')
        ).scalar_subquery()  # Получаем медиану как скалярное значение

        sold_stats_query = select(
            func.count().label('sold_count'),
            func.avg(sold_cte.c.price).label('average_price'),
            func.min(sold_cte.c.price).label('minimum_price'),
            func.max(sold_cte.c.price).label('maximum_price'),
            func.percentile_cont(0.5).within_group(func.abs(sold_cte.c.price - median_query)).label('mad')
        )

        count_summary = sold_stats_query.c.sold_count + unsold_cte.c.unsold_count + cancelled_cte.c.cancelled_count

        query = select(
            count_summary.label('count'),
            median_query.label('median'),
            cancelled_cte.c.cancelled_count,
            sold_stats_query.c.sold_count,
            sold_stats_query.c.average_price,
            sold_stats_query.c.minimum_price,
            sold_stats_query.c.maximum_price,
            unsold_cte.c.unsold_count,
            sold_stats_query.c.mad,
        )
        return query

    @staticmethod
    def get_stats_period_query(limit: int, item_id: str, quality: str = None) -> select:
        subquery = (
            select(Lots.post_id, Lots.stamp)
            .filter(Lots.item_id == literal(item_id))
            .order_by(Lots.stamp.desc())
            .limit(limit)
        )

        if quality is not None:
            if quality == 'Common':
                quality_condition = Lots.quality.is_(None)
            else:
                quality_condition = (Lots.quality == literal(quality))

            subquery = subquery.filter(quality_condition)

        subquery_cte = subquery.cte()

        query = select(
            func.min(subquery_cte.c.stamp).label('first_stamp'),  # Старейший лот, наименьший stamp
            func.max(subquery_cte.c.stamp).label('last_stamp'),  # Новейший лот, наибольший stamp
        )
        return query


class StatsRepository(StatsQueries):
    def __init__(self):
        self.session: Session

    def __enter__(self):
        """Инициализация сессии при входе в контекст."""
        self.session = Session()
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        """Закрытие сессии и обработка исключений."""
        try:
            if exc_type:
                self.session.rollback()  # В случае ошибок откатываем транзакцию
        finally:
            self.session.close()  # Всегда закрываем сессию

    def calculate_statistics(self, item_id: str, quality: str = None, stamp: int = None) -> SQLAlchemyRow:
        query = self.statistics_query(item_id, quality, stamp)
        return self.session.execute(query).fetchone()

    def get_stats_period(self, limit: int, item_id: str, quality: str = None) -> SQLAlchemyRow:
        query = self.get_stats_period_query(limit, item_id, quality)
        return self.session.execute(query).fetchone()

    def upsert_all_time_stats(
        self,
        item_id: str,
        quality: str,
        item_name: str,
        count: int,
        median: Decimal,
        cancelled_count: int,
        sold_count: int,
        average_price: Decimal,
        minimum_price: Decimal,
        maximum_price: Decimal,
        unsold_count: int,
        mad: Decimal,
    ) -> int:
        # Проверяем, существует ли запись
        stat_record = (
            self.session.query(AllTimeStats)
            .filter_by(item_id=item_id, quality=quality)
            .one_or_none()
        )

        if stat_record:
            # Если запись существует, обновляем значения
            stat_record.item_name = item_name
            stat_record.count = count if count else 0
            stat_record.median = median if median else 0
            stat_record.cancelled_count = cancelled_count if cancelled_count else 0
            stat_record.sold_count = sold_count if sold_count else 0
            stat_record.average_price = average_price if average_price else 0
            stat_record.minimum_price = minimum_price if minimum_price else 0
            stat_record.maximum_price = maximum_price if maximum_price else 0
            stat_record.unsold_count = unsold_count if unsold_count else 0
            stat_record.mad = mad if mad else 0
        else:
            # Если записи нет, создаем новую
            stat_record = AllTimeStats(
                item_id=item_id,
                quality=quality,
                item_name=item_name,
                count=count,
                median=median,
                cancelled_count=cancelled_count,
                sold_count=sold_count,
                average_price=average_price,
                minimum_price=minimum_price,
                maximum_price=maximum_price,
                unsold_count=unsold_count,
                mad=mad,
            )
            self.session.add(stat_record)
        self.session.commit()
        return stat_record.id

    def upsert_period_stats(
        self,
        stats_id: int,
        first_date: datetime,
        last_date: datetime,
        count: int,
        median: Decimal,
        cancelled_count: int,
        sold_count: int,
        average_price: Decimal,
        minimum_price: Decimal,
        maximum_price: Decimal,
        unsold_count: int,
        mad: Decimal,
    ) -> int:

        stat_record = (
            self.session.query(PeriodStats)
            .filter_by(stats_id=stats_id)
            .one_or_none()
        )

        if stat_record:
            stat_record.first_date = first_date
            stat_record.last_date = last_date
            stat_record.count = count if count else 0
            stat_record.median = median if median else 0
            stat_record.cancelled_count = cancelled_count if cancelled_count else 0
            stat_record.sold_count = sold_count if sold_count else 0
            stat_record.average_price = average_price if average_price else 0
            stat_record.minimum_price = minimum_price if minimum_price else 0
            stat_record.maximum_price = maximum_price if maximum_price else 0
            stat_record.unsold_count = unsold_count if unsold_count else 0
            stat_record.mad = mad if mad else 0
        else:
            stat_record = PeriodStats(
                stats_id=stats_id,
                first_date=first_date,
                last_date=last_date,
                count=count,
                median=median,
                cancelled_count=cancelled_count,
                sold_count=sold_count,
                average_price=average_price,
                minimum_price=minimum_price,
                maximum_price=maximum_price,
                unsold_count=unsold_count,
                mad=mad,
            )
            self.session.add(stat_record)
        self.session.commit()
        return stat_record.id
