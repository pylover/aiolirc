import asyncio
import unittest
from unittest.case import _Outcome


class AioTestCase(unittest.TestCase):

    # noinspection PyPep8Naming
    def __init__(self, *args, loop=None):
        self.loop = loop or asyncio.get_event_loop()
        super(AioTestCase, self).__init__(*args)
    #
    # def coroutine_function_decorator(self, func):
    #     def wrapper(*args, **kw):
    #         return self.loop.run_until_complete(func(*args, **kw))
    #     return wrapper
    #
    # def __getattribute__(self, item):
    #     attr = object.__getattribute__(self, item)
    #     if asyncio.iscoroutinefunction(attr):
    #         if item not in self._function_cache:
    #             self._function_cache[item] = self.coroutine_function_decorator(attr)
    #         return self._function_cache[item]
    #     return attr

    def _run_method(self, func, *args, **kwargs):
        if asyncio.iscoroutinefunction(func):
            return self.loop.run_until_complete(func(*args, **kwargs))
        else:
            return func(*args, **kwargs)

    def run(self, result=None):
        orig_result = result
        if result is None:
            result = self.defaultTestResult()
            startTestRun = getattr(result, 'startTestRun', None)
            if startTestRun is not None:
                startTestRun()

        result.startTest(self)

        testMethod = getattr(self, self._testMethodName)
        if (getattr(self.__class__, "__unittest_skip__", False) or
            getattr(testMethod, "__unittest_skip__", False)):
            # If the class or method was skipped.
            try:
                skip_why = (getattr(self.__class__, '__unittest_skip_why__', '')
                            or getattr(testMethod, '__unittest_skip_why__', ''))
                self._addSkip(result, self, skip_why)
            finally:
                result.stopTest(self)
            return
        expecting_failure_method = getattr(testMethod,
                                           "__unittest_expecting_failure__", False)
        expecting_failure_class = getattr(self,
                                          "__unittest_expecting_failure__", False)
        expecting_failure = expecting_failure_class or expecting_failure_method
        outcome = _Outcome(result)
        try:
            self._outcome = outcome

            with outcome.testPartExecutor(self):
                self._run_method(self.setUp)
            if outcome.success:
                outcome.expecting_failure = expecting_failure
                with outcome.testPartExecutor(self, isTest=True):
                    self._run_method(testMethod)
                outcome.expecting_failure = False
                with outcome.testPartExecutor(self):
                    self._run_method(self.tearDown)

            self.doCleanups()
            for test, reason in outcome.skipped:
                self._addSkip(result, test, reason)
            self._feedErrorsToResult(result, outcome.errors)
            if outcome.success:
                if expecting_failure:
                    if outcome.expectedFailure:
                        self._addExpectedFailure(result, outcome.expectedFailure)
                    else:
                        self._addUnexpectedSuccess(result)
                else:
                    result.addSuccess(self)
            return result
        finally:
            result.stopTest(self)
            if orig_result is None:
                stopTestRun = getattr(result, 'stopTestRun', None)
                if stopTestRun is not None:
                    stopTestRun()

            # explicitly break reference cycles:
            # outcome.errors -> frame -> outcome -> outcome.errors
            # outcome.expectedFailure -> frame -> outcome -> outcome.expectedFailure
            outcome.errors.clear()
            outcome.expectedFailure = None

            # clear the outcome, no more needed
            self._outcome = None



