# event_face_app

## Синхронизация

### Полная
```commandline
uv run python manage.py sync_events --all
```
### Инкрементальная
```commandline
uv run python manage.py sync_events
```

## Transactional Outbox

### Воркер для отправки уведомлений
```commandline
uv run python manage.py process_outbox
```

## Очистка старых мероприятий

### Удаляет события старше 7 дней после event_time.
```commandline
uv run python manage.py cleanup_events
```


