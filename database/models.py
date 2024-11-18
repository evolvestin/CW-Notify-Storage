from database.session import engine
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import (
    String, ForeignKey, Numeric, DateTime, BigInteger, Column, Index, Integer, PrimaryKeyConstraint, Text
)


Base = declarative_base()


class Lots(Base):
    __tablename__ = 'lots'

    post_id = Column(Integer, primary_key=True, nullable=False, default=0)
    lot_id = Column(Integer, nullable=False, default=0)
    item_id = Column(Text, nullable=True)
    item_name = Column(Text, nullable=True)
    item_emoji = Column(Text, nullable=True)
    enchant = Column(Integer, nullable=True, default=None)
    left_engrave = Column(Text, nullable=True)
    right_engrave = Column(Text, nullable=True)
    params = Column(Text, nullable=True)
    quality = Column(Text, nullable=True)
    condition = Column(Text, nullable=True)
    modifiers = Column(Text, nullable=True)
    seller_castle = Column(Text, nullable=True)
    seller_emoji = Column(Text, nullable=True)
    seller_guild = Column(Text, nullable=True)
    seller_name = Column(Text, nullable=True)
    price = Column(Integer, nullable=False, default=0)
    buyer_castle = Column(Text, nullable=True)
    buyer_emoji = Column(Text, nullable=True)
    buyer_guild = Column(Text, nullable=True)
    buyer_name = Column(Text, nullable=True)
    stamp = Column(BigInteger, nullable=False, default=0)
    status = Column(Text, nullable=True)

    __table_args__ = (
        PrimaryKeyConstraint('post_id', name='post_id_primary_key'),
        Index('index_lot_id', 'lot_id'),
        Index('index_item_id', 'item_id')
    )


class AllTimeStats(Base):
    __tablename__ = 'all_time_stats'

    id = Column(Integer, primary_key=True)
    item_id = Column(String, nullable=False)
    quality = Column(String, nullable=True)
    item_name = Column(String, nullable=False)
    count = Column(Integer, nullable=False, default=0)
    median = Column(Numeric(24, 12), nullable=False, default=0)
    cancelled_count = Column(Integer, nullable=False, default=0)
    sold_count = Column(Integer, nullable=False, default=0)
    average_price = Column(Numeric(24, 12), nullable=False, default=0)
    minimum_price = Column(Numeric(24, 12), nullable=False, default=0)
    maximum_price = Column(Numeric(24, 12), nullable=False, default=0)
    unsold_count = Column(Integer, nullable=False, default=0)
    mad = Column(Numeric(24, 12), nullable=False, default=0)

    period_stats = relationship('PeriodStats', back_populates='all_time_stats')


class PeriodStats(Base):
    __tablename__ = 'period_stats'

    id = Column(Integer, primary_key=True)
    stats_id = Column(Integer, ForeignKey('all_time_stats.id'), nullable=False)
    first_date = Column(DateTime, nullable=False)
    last_date = Column(DateTime, nullable=False)
    count = Column(Integer, nullable=False, default=0)
    median = Column(Numeric(24, 12), nullable=False, default=0)
    cancelled_count = Column(Integer, nullable=False, default=0)
    sold_count = Column(Integer, nullable=False, default=0)
    average_price = Column(Numeric(24, 12), nullable=False, default=0)
    minimum_price = Column(Numeric(24, 12), nullable=False, default=0)
    maximum_price = Column(Numeric(24, 12), nullable=False, default=0)
    unsold_count = Column(Integer, nullable=False, default=0)
    mad = Column(Numeric(24, 12), nullable=False, default=0)

    all_time_stats = relationship('AllTimeStats', back_populates='period_stats')


Base.metadata.create_all(bind=engine, tables=[AllTimeStats.__table__, PeriodStats.__table__])
