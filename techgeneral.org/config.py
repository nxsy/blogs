config.register_asset(
    'main_css',
    'reset.css',
    'main.css',
    'pygment.css',
    output="cache_main.%(version)s.css")

config.context_update(
    name="TechGeneral",
    url="https://techgeneral.org",
    fb_app_id="664060780373796",
)
