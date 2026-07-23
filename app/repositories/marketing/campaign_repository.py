from sqlalchemy.orm import Session

from app.models.marketing.campaign import Campaign


class CampaignRepository:

    def __init__(self, db: Session):
        self.db = db


    def create(
        self,
        campaign: Campaign,
    ):
        self.db.add(campaign)
        self.db.commit()
        self.db.refresh(campaign)

        return campaign


    def get_by_id(
        self,
        campaign_id: int,
        user_id: int,
    ):
        return (
            self.db.query(Campaign)
            .filter(
                Campaign.id == campaign_id,
                Campaign.user_id == user_id,
            )
            .first()
        )


    def get_all(
        self,
        user_id: int,
    ):
        return (
            self.db.query(Campaign)
            .filter(
                Campaign.user_id == user_id,
            )
            .order_by(
                Campaign.id.desc()
            )
            .all()
        )


    def update(
        self,
        campaign: Campaign,
    ):
        self.db.commit()
        self.db.refresh(campaign)

        return campaign


    def delete(
        self,
        campaign: Campaign,
    ):
        self.db.delete(campaign)
        self.db.commit()

        return True
