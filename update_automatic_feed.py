from datetime import datetime

from services.feed_service import merge_prom_feeds
from services.merge_available_products import merge_available_products_feeds
from services.delete_item_from_trinity_price import filter_trinity_feed
from services.exceptions import FeedError


def main() -> None:
    print("=" * 60)
    print(f"Початок оновлення: {datetime.now()}")

    errors = []

    # Оновлення VIATEC
    print("\nОновлення VIATEC")

    try:
        merge_available_products_feeds()
        feed_path = merge_prom_feeds()

        print(f"VIATEC: готовий XML — {feed_path}")

    except FeedError as error:
        print(f"VIATEC: помилка оновлення — {error}")
        errors.append("VIATEC")

    # Оновлення Trinity
    print("\nОновлення Trinity")

    try:
        trinity_path = filter_trinity_feed()

        print(f"Trinity: готовий XML — {trinity_path}")

    except FeedError as error:
        print(f"Trinity: помилка оновлення — {error}")
        errors.append("Trinity")

    # Результат оновлення
    print(f"\nЗавершено: {datetime.now()}")

    if errors:
        print(f"Помилки оновлення: {', '.join(errors)}")
    else:
        print("Усі прайс-листи успішно оновлено.")

    print("=" * 60)

    if errors:
        raise SystemExit(1)


if __name__ == "__main__":
    main()