import math
from datetime import datetime
from database.repository import StatsRepository


def update_statistics(item: dict):
    print('UPDATING', item)
    with StatsRepository() as db:
        stats = db.calculate_statistics(item['item_id'], item['quality'])
        stats_record_id = db.upsert_all_time_stats(
            item_id=item['item_id'],
            quality=item['quality'],
            item_name=item['item_name'],
            count=stats.count,
            median=stats.median,
            cancelled_count=stats.cancelled_count,
            sold_count=stats.sold_count,
            average_price=stats.average_price,
            minimum_price=stats.minimum_price,
            maximum_price=stats.maximum_price,
            unsold_count=stats.unsold_count,
            mad=stats.mad,
        )

        limited_lots_count = math.ceil(math.sqrt(stats.count))

        if limited_lots_count > 5:
            period = db.get_stats_period(limited_lots_count, item['item_id'], item['quality'])
            limited_stats = db.calculate_statistics(item['item_id'], item['quality'], stamp=period.first_stamp)
            db.upsert_period_stats(
                stats_id=stats_record_id,
                first_date=datetime.fromtimestamp(period.first_stamp),
                last_date=datetime.fromtimestamp(period.last_stamp),
                count=limited_stats.count,
                median=limited_stats.median,
                cancelled_count=limited_stats.cancelled_count,
                sold_count=limited_stats.sold_count,
                average_price=limited_stats.average_price,
                minimum_price=limited_stats.minimum_price,
                maximum_price=limited_stats.maximum_price,
                unsold_count=limited_stats.unsold_count,
                mad=limited_stats.mad,
            )
