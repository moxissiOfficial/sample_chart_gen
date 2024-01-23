from datetime import datetime, timedelta
import pytz
import pandas


class BerlinTime:
    def __init__(self) -> None:
        pass

    def getTime(self, T: pandas.Series, t: int) -> str:
        """
        Method returning date and time in Berlin
        time zone from UNIX timestamp.
        """

        if isinstance(T, pandas.core.series.Series):
            T = T.iloc[0]
        else:
            pass
        timestamp_utc = datetime.utcfromtimestamp(T) + timedelta(milliseconds=t)

        utc_timezone = pytz.timezone("UTC")
        timestamp_utc = utc_timezone.localize(timestamp_utc)

        berlin_timezone = pytz.timezone("Europe/Berlin")
        # berlin_timezone = pytz.timezone("Europe/London")
        berlin_time = timestamp_utc.astimezone(berlin_timezone)

        # Format the output without timezone information
        formatted_output = berlin_time.strftime("%d.%m.%Y %H:%M:%S.%f")[
            :-3
        ]  # Remove last three digits of microseconds

        return formatted_output
