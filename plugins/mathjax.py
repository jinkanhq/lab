from pelican import signals


def enable_mathjax(sender):
    """
    Enable ``math_output`` of docuitls with a trick.
    See http://docs.mathjax.org/en/latest/web/configuration.html
    """
    docutils_settings = sender.settings.get("DOCUTILS_SETTINGS", {})
    docutils_settings.setdefault(
        "math_output", f"mathjax 1"
    )
    sender.settings["DOCUTILS_SETTINGS"] = docutils_settings


def register():
    signals.initialized.connect(enable_mathjax)
