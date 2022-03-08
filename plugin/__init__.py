# import all listeners and commands
from .commands.rfc_copy_rich_codes import RfcCopyRichCodesCommand

__all__ = (
    # ST: core
    "plugin_loaded",
    "plugin_unloaded",
    # ST: commands
    "RfcCopyRichCodesCommand",
)


def plugin_loaded() -> None:
    pass


def plugin_unloaded() -> None:
    pass
