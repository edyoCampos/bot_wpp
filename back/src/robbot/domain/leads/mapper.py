from robbot.domain.leads.lead import Lead
from robbot.domain.shared.value_objects import LeadScore, PhoneNumber
from robbot.infra.persistence.models.lead_model import LeadModel


class LeadMapper:
    @staticmethod
    def to_domain(model: LeadModel) -> Lead:
        return Lead(
            id=model.id,
            name=model.name,
            phone_number=PhoneNumber(model.phone_number),
            status=model.status,
            maturity_score=LeadScore(model.maturity_score),
            email=model.email,
            assigned_to_user_id=model.assigned_to_user_id,
            created_at=model.created_at,
            updated_at=model.updated_at,
            converted_at=model.converted_at,
            deleted_at=getattr(model, "deleted_at", None),
        )

    @staticmethod
    def to_model(entity: Lead, model: LeadModel | None = None) -> LeadModel:
        if model is None:
            model = LeadModel(id=entity.id)
        
        model.name = entity.name
        model.phone_number = entity.phone_number.value
        model.status = entity.status
        model.maturity_score = entity.maturity_score.value
        model.email = entity.email
        model.assigned_to_user_id = entity.assigned_to_user_id
        model.created_at = entity.created_at
        model.updated_at = entity.updated_at
        model.converted_at = entity.converted_at
        if hasattr(model, "deleted_at"):
            model.deleted_at = entity.deleted_at
            
        return model
