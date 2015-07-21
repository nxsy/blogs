config.register_asset(
    'main_css',
    'reset.css',
    'main.css',
    'pygment.css',
    output="cache_main.%(version)s.css")

config.context_update(
    name="play.TechGeneral",
    url="http://play.techgeneral.org",
    fb_app_id="641472525895652",
)
