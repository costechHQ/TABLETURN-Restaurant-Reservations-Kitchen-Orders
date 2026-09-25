def log_webhook_processed(
    event_id: str,
    reference: str,
) -> None:
    print(
        f"Background task: webhook processed "
        f"event_id={event_id}, reference={reference}"
    )