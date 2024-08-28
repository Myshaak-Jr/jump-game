from gui import SliderElement


SliderElement(app_state.width / 4, min=0, max=100, default=100, step=1,
	on_change=lambda value: log.info(f"Master volume: {value}")
)
