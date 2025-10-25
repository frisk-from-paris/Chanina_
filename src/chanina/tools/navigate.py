""" tools for navigating a page.
functions do not return anything but make the current_page to the desired state.
"""
from typing import Literal

from chanina.tools._meta_tools import normalize_url


class Navigate:
    def __init__(self, session) -> None:
        self.session = session

    def goto(
        self,
        url: str,
        timeout: int = 15000,
        allow_redirect: bool = True,
        wait_event: Literal[
            "load",
            "domcontentloaded",
            "commit",
            "networkidle"
        ] = "networkidle"
    ) -> None:
        """
        Go to the desired url and assure the page is fully loaded in a timely manner.
    
        Args:
            - url (str): url to go to.
            - timeout (float): max timeout to wait for the page to load (ms).
            - allow_redirect (bool): If set to False, raise Exception if page is redirected.
            - wait_event (Literal[str]): event to wait until.
        """
        url = normalize_url(url)
        response = self.session.current_page.goto(url, timeout=timeout, wait_until=wait_event)
        self.session.current_page.wait_for_load_state(wait_event)
        if not response:
            raise Exception(f"did not get response from {url}.")
        #if not response.status in range(200, 299):
        #    raise Exception(f"got status code : {response.status}.")
        if not allow_redirect and not response.url == url:
            raise Exception(f"unauthorized rediction to {response.url}.")
    
    
    def scroller(
        self,
        container: str,
        attribute: str = "id",
        axis: Literal['y', 'x'] = 'y',
        reload_timeout: int = 2000,
        max_reload: int = 0,
        speed: int = 50
    ) -> None:
        """
        scroll all the way down a scroll bar.
    
        Args:
            - container(str): the container for the scrollbar(s). Set to ':root' for whole document.
            - axis (Literal['y', 'x']): scrolling axis.
            - reload_timeout (int): for dynamically generated content.
                    If a value is set, waits 'reload_timeout' ms and check if scroll_bar is still maxed.
            - max_reload (int): maximum reloading allowed. -1 is for reload until finished.
            - attribute (str): which attribute to match the scroll_bar.
        """
        page = self.session.current_page
    
        if attribute == "class":
            js_get_element = f'document.querySelector(".{container}")'
        else:
            js_get_element = f'document.querySelector("[{attribute}=\\"{container}\\"]")'
    
        if container == ":root":
            js_get_element = f'document.documentElement'
    
        el = page.evaluate_handle(js_get_element)
    
        if not el:
            raise Exception(f"'{container}' does not exist on current page.")
    
        def get_scroll_pos():
            return page.evaluate(f"(el) => el.{axis_scroll}", el)
    
        def get_scroll_size():
            return page.evaluate(f"(el) => el.{axis_size}", el)
    
        def get_client_size():
            return page.evaluate(f"(el) => el.{axis_client}", el)
    
        axis_scroll = "scrollTop" if axis == "y" else "scrollLeft"
        axis_size = "scrollHeight" if axis == "y" else "scrollWidth"
        axis_client = "clientHeight" if axis == "y" else "clientWidth"
        previous_pos = get_scroll_pos()
        client_size = get_client_size()
        scroll_size = get_scroll_size()
    
        if scroll_size <= client_size:
            raise Exception(f"'{container}' does not have a scroll bar.")
    
        reload_count = 0
    
        while True:
            page.evaluate(f"(el) => el.{axis_scroll} += {speed}", el)
            current_pos = get_scroll_pos()
    
            if current_pos == previous_pos:
                if reload_timeout == 0:
                    break
                page.wait_for_timeout(reload_timeout)
                page.evaluate(f"(el) => el.{axis_scroll} += 50", el)
                current_pos = get_scroll_pos()
                if current_pos == previous_pos:
                    reload_count += 1
                    if max_reload != -1 and reload_count >= max_reload:
                        break
                    else:
                        continue
            previous_pos = current_pos
