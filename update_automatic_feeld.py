from datetime import datetime

from services.feed_service import FeedError, merge_prom_feeds


def main() -> None:
    print("=" * 60)
    print(f"Початок оновлення: {datetime.now()}")

    try:
        feed_path = merge_prom_feeds()

    except FeedError as error:
        print(f"Оновлення не виконано: {error}")
        raise

    print(f"Готовий XML: {feed_path}")
    print(f"Завершено: {datetime.now()}")
    print("=" * 60)


if __name__ == "__main__":
    main()