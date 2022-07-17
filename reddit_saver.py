import argparse
import csv
import enum
import logging
import urllib.parse

import praw

logger = logging.getLogger(__name__)


@enum.unique
class ItemType(enum.Enum):
    link = "Link"
    comment = "Comment"


def _parse_args() -> argparse.Namespace:
    """
    Parse CLI arguments

    :return: The parsed CLI arguments
    :rtype: argparse.Namespace
    """
    logger.debug("Parsing CLI arguments")
    parser = argparse.ArgumentParser(
        description="Tool to save down an accounts saved posts on reddit"
    )
    parser.add_argument(
        "--target_file",
        type=str,
        required=True,
        help="The file to write the results to",
    )
    parser.add_argument(
        "--log_level",
        type=str,
        default="INFO",
        choices=["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"],
    )
    args = parser.parse_args()
    logger.debug("Finished parsing CLI arguments")
    return args


def _write_header(saved_writer) -> None:
    """
    Write the column headers
    """
    saved_writer.writerow(["title", "url", "type"])


def _handle_item(item, saved_writer) -> None:
    if isinstance(item, praw.models.reddit.comment.Comment):  # Comment
        item_type = ItemType.link
        logger.info(f"{item!r} is a {item_type}")
        saved_writer.writerow(
            [
                item.link_title,
                urllib.parse.urljoin("https://reddit.com", item.permalink),
                ItemType.comment.value,
            ]
        )
    else:  # Link
        item_type = ItemType.link
        logger.info(f"{item!r} is a {item_type}")
        saved_writer.writerow([item.title, item.url, ItemType.link.value])


def main() -> None:
    """
    Main entrypoint
    """
    args = _parse_args()
    logging.basicConfig(
        format="[%(asctime)s] {%(pathname)s:%(lineno)d} %(levelname)s - %(message)s",
        level=args.log_level,
    )

    reddit = praw.Reddit("saver_bot")
    logger.info("Logged in")

    with open(args.target_file, "w", newline="") as csvfile:
        logger.info(f"Writing results to {args.target_file}")
        saved_writer = csv.writer(csvfile, delimiter=",", quoting=csv.QUOTE_MINIMAL)
        _write_header(saved_writer)
        for item in reddit.user.me().saved(limit=None):
            _handle_item(item, saved_writer)


if __name__ == "__main__":
    main()
