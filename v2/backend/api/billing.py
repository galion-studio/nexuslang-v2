@router.get("/admin/profitability")
async def get_profitability_report(
    days: int = 30,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get profitability report (admin only).

    Shows revenue, costs, and profit margins.
    """
    if not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required"
        )

    from ..services.billing.credit_service import get_credit_service
    credit_service = get_credit_service(db)

    return credit_service.get_profitability_report(days)

@router.get("/pricing/packages")
async def get_credit_packages():
    """
    Get available credit packages for purchase.

    Returns all credit packages with pricing and margins.
    """
    from ..services.billing.credit_service import CreditService

    return {
        "packages": CreditService.CREDIT_PACKAGES,
        "margins": {
            "minimum": "87%",
            "average": "91%",
            "maximum": "93.5%"
        },
        "note": "All packages include volume discounts for better value"
    }

@router.get("/pricing/subscriptions")
async def get_subscription_pricing():
    """
    Get subscription pricing tiers.

    Returns all subscription tiers with features and pricing.
    """
    from ..services.billing.credit_service import CreditService

    return {
        "tiers": CreditService.SUBSCRIPTION_PRICING,
        "features": SUBSCRIPTION_TIERS,
        "billing": "Monthly recurring billing, cancel anytime"
    }