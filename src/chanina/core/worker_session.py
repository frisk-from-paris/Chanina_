import os

from chanina.utils import log
from chanina.tools import inspect, interact, navigate, filters, wait

from playwright.sync_api import Page, Playwright, sync_playwright


class WorkerSession:
    def __init__(
        self,
        caller_path: str,
        headless: bool,
        browser_name: str,
        profile: str = ""
    ) -> None:
        """
        The 'WorkerSession' object is a shared IN MEMORY object between every tasks inside a
        same worker. This means that this object is not serialized, but lives in memory in the
        same space as every other tasks and processes inside the current worker.

        We start a playwright session here, which will live as long as this WorkerSession
        lives.
        """
        # Starting playwright process ...
        log(f"[WorkerSession] Running playwright from dir : '{caller_path}'")
        self._pw = sync_playwright().start()

        self._current_page = None
        self._browser_name = browser_name
        self._profile = profile
        self._headless = headless
        self._profile_path = os.path.abspath(profile)

        self._init_context()

        # Those attributes will be populated by the _init_tools method.
        self.navigate: navigate.Navigate 
        self.filters : filters.Filters
        self.inspect: inspect.Inspect
        self.interact: interact.Interact
        self.wait: wait.Wait

        # Initializes the tools.
        self._init_tools()

        log("[WorkerSession] Initialized")

    @property
    def playwright(self) -> Playwright:
        """ Return playwright context. """
        return self._pw

    @property
    def current_page(self) -> Page | None:
        """ Return the last created page. """
        return self._current_page

    def _init_context(self) -> None:
        """
        Function to initialize the browser_context.
        Depending on the profile and browser_name.
        """
        if self._browser_name == "firefox":
            if self._profile:
                log(f"[WorkerSession] Launching firefox with persistent context. (profile: '{self._profile_path}')")
                self.browser_context = self._pw.firefox.launch_persistent_context(
                    user_data_dir=self._profile_path,
                    headless=self._headless
                )
            else:
                log("[WorkerSession] Launching firefox.")
                self.browser_context = self._pw.firefox.launch(headless=self._headless).new_context()
        elif self._browser_name == "chrome":
            log("[WorkerSession] Launching Chrome")
            self.browser_context = self._pw.chromium.launch(headless=self._headless).new_context()
        else:
            raise ValueError("Browser must be 'firefox' or 'chrome'")

    def _init_tools(self) -> None:
        """
        For ease of developpment, usage and maintaining, tools are objects that performs
        cool operations inside the current_context, alway on the current page.
        """
        self.navigate = navigate.Navigate(self)
        self.filters = filters.Filters(self)
        self.inspect = inspect.Inspect(self)
        self.interact = interact.Interact(self)
        self.wait = wait.Wait(self)

    def get_current_page(self, required: bool = True) -> Page:
        """
        Return the current_page.
        If required is True (default), raises an exception if current_page is None
        """
        if required and not self._current_page:
            raise Exception("Trying to access the current_page that doesn't exist.")
        return self.current_page if self.current_page else Page({}) # Linter is pissing me off

    def new_page(self) -> Page:
        """ Create a new page, overrides the '_current_page'. """
        self._current_page = self.browser_context.new_page()
        return self._current_page

    def close_page(self) -> None:
        """ Close the 'current_page'."""
        self.get_current_page().close()
        self._current_page = None

    def close(self) -> None:
        """ Close the context. """
        try:
            self.browser_context.close()
        except Exception as e:
            log(f"[WorkerSession] Closed with an exception : {e}")
        self._pw.stop()
        log("[WorkerSession] Stopped.")
