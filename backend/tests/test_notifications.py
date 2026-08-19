import pytest
from backend.services.notification_service import notification_service

def test_notification_lifecycle(client):
    clerk_id = "test_user_notif_123"
    
    # 1. Create notifications
    notif_id_1 = notification_service.create_notification(
        clerk_id=clerk_id,
        type="prediction_complete",
        title="Prediction Ready",
        message="Your multi-disease assessment is complete.",
        severity="info"
    )
    assert notif_id_1 is not None

    notif_id_2 = notification_service.create_notification(
        clerk_id=clerk_id,
        type="risk_alert",
        title="High Risk Detected",
        message="Cardiovascular risk is elevated.",
        severity="critical"
    )
    assert notif_id_2 is not None

    # 2. Query user notifications
    items, unread_count = notification_service.get_user_notifications(clerk_id)
    assert len(items) >= 2
    assert unread_count >= 2

    # 3. Mark one as read
    marked = notification_service.mark_as_read(clerk_id, notif_id_1)
    assert marked is True

    items_after, unread_after = notification_service.get_user_notifications(clerk_id)
    assert unread_after == unread_count - 1

    # 4. Mark all as read
    updated_count = notification_service.mark_all_as_read(clerk_id)
    assert updated_count >= 1

    items_final, unread_final = notification_service.get_user_notifications(clerk_id)
    assert unread_final == 0

def test_dispatch_prediction_notifications(client):
    clerk_id = "test_user_dispatch_456"
    results = {
        "heart": 75.0,
        "diabetes": 20.0,
        "kidney": 15.0
    }
    
    notification_service.dispatch_prediction_notifications(clerk_id, "pred_789", results)
    
    items, unread_count = notification_service.get_user_notifications(clerk_id)
    # Should create both completion and high risk alert (since heart >= 50%)
    types = [item["type"] for item in items]
    assert "prediction_complete" in types
    assert "risk_alert" in types
