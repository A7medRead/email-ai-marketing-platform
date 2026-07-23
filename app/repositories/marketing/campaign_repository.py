from sqlalchemy.orm import Session

from app.models.marketing.campaign import Campaign


class CampaignRepository:

    def __init__(
        self,
        db: Session,
    ):
        self.db = db


    def create(
        self,
        campaign: Campaign,
    ):
        self.db.add(campaign)
        self.db.commit()
        self.db.refresh(campaign)

        return campaign


    def get_all(
        self,
        user_id: int,
    ):
        return (
            self.db.query(Campaign)
            .filter(
                Campaign.user_id == user_id
            )
            .all()
        )


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


    def update(
        self,
        campaign_id: int,
        user_id: int,
        data: dict,
    ):

        campaign = self.get_by_id(
            campaign_id,
            user_id,
        )

        if not campaign:
            return None


        for key, value in data.items():
            setattr(
                campaign,
                key,
                value,
            )


        self.db.commit()
        self.db.refresh(campaign)

        return campaign


    def delete(
        self,
        campaign_id: int,
        user_id: int,
    ):

        campaign = self.get_by_id(
            campaign_id,
            user_id,
        )

        if not campaign:
            return False


        self.db.delete(campaign)
        self.db.commit()

        return True



def get_campaign_by_id(
    db: Session,
    campaign_id: int,
    user_id: int,
):

    return (
        db.query(Campaign)
        .filter(
            Campaign.id == campaign_id,
            Campaign.user_id == user_id,
        )
        .first()
    )
