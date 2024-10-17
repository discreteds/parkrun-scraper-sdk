import requests
from bs4 import BeautifulSoup
import math
import time


def _create_session():
    session = requests.Session()
    session.headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:93.0) Gecko/20100101 Firefox/93.0",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.5",
        "Accept-Encoding": "gzip, deflate, br",
        "DNT": "1",
        "Connection": "keep-alive",
        "Upgrade-Insecure-Requests": "1",
        "Sec-Fetch-Dest": "document",
        "Sec-Fetch-Mode": "navigate",
        "Sec-Fetch-Site": "none",
        "Sec-Fetch-User": "?1"
    }

    return session

class BaseScraper:

    session: requests.Session

    @classmethod
    def create_session(cls):

        session = requests.Session()
        session.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:93.0) Gecko/20100101 Firefox/93.0",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.5",
            "Accept-Encoding": "gzip, deflate, br",
            "DNT": "1",
            "Connection": "keep-alive",
            "Upgrade-Insecure-Requests": "1",
            "Sec-Fetch-Dest": "document",
            "Sec-Fetch-Mode": "navigate",
            "Sec-Fetch-Site": "none",
            "Sec-Fetch-User": "?1"
        }

        cls.session = session

    @classmethod
    def init_session(cls, session=None):

        if session is not None:
            cls.session = session

        if cls.session is None:
            BaseScraper.create_session()



class Country(BaseScraper):

    session: requests.Session


    def __init__(self, _id=None, _url=None, session=None):

        self.init_session(session)

        self.id = _id
        self.url = _url

        pass

    @classmethod
    def GetAllCountries(cls):

        cls.init_session()

        countries = []

        countriesJson = cls.session.get("https://images.parkrun.com/events.json").json()["countries"]

        for countryKey in countriesJson:

            country = Country(
                _id=countryKey, 
                _url= f"https://{countriesJson[countryKey]["url"]}"
                )

            countries.append(country)

        return countries

class Event(BaseScraper):

    def __init__(self, _id=None, _name=None, _longName=None, _shortName=None, _countryCode=None, _seriesId=None, _location=None, _url=None, session=None):

        self.init_session(session)

        self.id = _id
        self.name = _name
        self.longName = _longName
        self.shortName = _shortName
        self.countryCode = _countryCode
        self.seriesId = _seriesId
        self.location = _location
        self.url = _url
        
        pass

    @classmethod
    def GetAllEvents(cls):

        cls.init_session()

        events = []

        eventsJson = cls.session.get("https://images.parkrun.com/events.json").json()["events"]["features"]

        for event in eventsJson:

            event = Event(
                _id=event["id"], 
                _name=event["properties"]["eventname"], 
                _longName=event["properties"]["EventLongName"], 
                _shortName=event["properties"]["EventShortName"], 
                _countryCode=event["properties"]["countrycode"], 
                _seriesId=event["properties"]["seriesid"], 
                _location=event["properties"]["EventLocation"]
                )

            events.append(event)

        return events

    @classmethod
    def UpdateEventUrls(cls, events, countries):


        for country in countries:

            for event in events:

                if str(event.countryCode) == str(country.id):

                    event.url = f"{country.url}/{event.name}/"

        return events

class Result(BaseScraper):

    def __init__(self, _name=None, _ageGroup=None, _club=None, _gender=None, _position=None, _runs=None, _ageGrade=None, _achievement=None, session=None):

        self.init_session(session)



        self.name = _name
        self.ageGroup = _ageGroup
        self.club = _club
        self.gender = _gender
        self.position = _position
        self.runs = _runs
        self.ageGrade = _ageGrade
        self.achievement = _achievement

        pass

    @classmethod
    def GetResults(cls, event, eventNumber):

        results = []

        resultsHTML = cls.session.get(event.url + "results/{eventNumber}/").text

        resultsSoup = BeautifulSoup(resultsHTML, "html.parser")
        resultRows = resultsSoup.findAll("tr", {"class": "Results-table-row"})

        for resultRow in resultRows:

            result = Result(
                _name=resultRow["data-name"],
                _ageGroup=resultRow["data-agegroup"],
                _club=resultRow["data-club"],
                _gender=resultRow["data-gender"],
                _position=resultRow["data-position"],
                _runs=resultRow["data-runs"],
                _ageGrade=resultRow["data-agegrade"],
                _achievement=resultRow["data-achievement"]
            )

            results.append(result)

        return results

    @classmethod
    def GetLatestResults(cls, event):

        return Result.GetResults(event, "latestresults")

class EventHistory(BaseScraper):

    def __init__(self, _eventNumber=None, _date=None, _finishers=None, _volunteers=None, _male=None, _female=None, _maleTime=None, _femaleTime=None, session=None):

        self.init_session(session)



        self.eventNumber = _eventNumber
        self.date = _date
        self.finishers = _finishers
        self.volunteers = _volunteers
        self.male = _male
        self.female = _female
        self.maleTime = _maleTime
        self.femaleTime = _femaleTime

        pass

    @classmethod
    def GetEventHistorys(cls, event):

        cls.init_session()

        eventHistorys = []

        eventHistoryHTML = cls.session.get(event.url + "results/eventhistory/").text

        eventHistorySoup = BeautifulSoup(eventHistoryHTML, "html.parser")
        eventHistoryRows = eventHistorySoup.findAll("tr", {"class": "Results-table-row"})

        for eventHistoryRow in eventHistoryRows:

            eventHistory = EventHistory(
                _eventNumber=eventHistoryRow["data-parkrun"],
                _date=eventHistoryRow["data-date"],
                _finishers=eventHistoryRow["data-finishers"],
                _volunteers=eventHistoryRow["data-volunteers"],
                _male=eventHistoryRow["data-male"],
                _female=eventHistoryRow["data-female"],
                _maleTime=eventHistoryRow["data-maletime"],
                _femaleTime=eventHistoryRow["data-femaletime"],
            )

            eventHistorys.append(eventHistory)

        return eventHistorys

class FirstFinisher(BaseScraper):

    def __init__(self, _parkRunner=None, _firstPlaceFinishes=None, _bestTime=None, _sex=None, session=None):

        self.init_session(session)


        self.parkRunner = _parkRunner
        self.firstPlaceFinishes = _firstPlaceFinishes
        self.bestTime = _bestTime
        self.sex = _sex

        pass

    @classmethod
    def GetFirstFinishers(cls, event):

        cls.init_session()


        firstFinishers = []

        firstFinishersHTML = cls.session.get(event.url + "results/firstfinishescount/").text

        firstFinishersSoup = BeautifulSoup(firstFinishersHTML, "html.parser")
        firstFinishersRows = firstFinishersSoup.find("table", {"id": "results"}).find("tbody").findAll("tr")

        for firstFinisherRow in firstFinishersRows:

            rowData = firstFinisherRow.findAll("td")

            firstFinisher = FirstFinisher(
                _parkRunner=rowData[0].find("a").text if rowData[0].find("a") else None,
                _firstPlaceFinishes=rowData[1].text if rowData[1] else None,
                _bestTime=rowData[2].text if rowData[2] else None,
                _sex=rowData[3].text if rowData[3] else None
            )

            firstFinishers.append(firstFinisher)

        return firstFinishers

class AgeCategoryRecord(BaseScraper):

    def __init__(self, _ageCategory=None, _eventNumber=None, _date=None, _parkRunner=None, _time=None, _ageGrade=None, session=None):

        self.init_session(session)


        self.ageCategory = _ageCategory
        self.eventNumber = _eventNumber
        self.date = _date
        self.parkRunner = _parkRunner
        self.time = _time
        self.ageGrade = _ageGrade

        pass

    @classmethod
    def GetAgeCategoryRecords(cls, event):

        cls.init_session()

        getAgeCategoryRecords = []

        getAgeCategoryRecordsHTML = cls.session.get(event.url + "results/agecategoryrecords/").text

        getAgeCategoryRecordsSoup = BeautifulSoup(getAgeCategoryRecordsHTML, "html.parser")
        getAgeCategoryRecordsRows = getAgeCategoryRecordsSoup.find("table", {"id": "results"}).find("tbody").findAll("tr")

        for ageCategoryRecordRow in getAgeCategoryRecordsRows:

            rowData = ageCategoryRecordRow.findAll("td")

            ageCategoryRecord = AgeCategoryRecord(
                _ageCategory=rowData[0].find("a").find("strong").text if rowData[0].find("a") else None,
                _eventNumber=rowData[2].find("a").text if rowData[2].find("a") else None,
                _date=rowData[3].find("a").text if rowData[3].find("a") else None,
                _parkRunner=rowData[4].text if rowData[4] else None,
                _time=rowData[5].text if rowData[5] else None,
                _ageGrade=rowData[6].text if rowData[6] else None
            )

            getAgeCategoryRecords.append(ageCategoryRecord)

        return getAgeCategoryRecords

class Club(BaseScraper):

    def __init__(self, _name=None, _numberOfParkrunners=None, _numberOfRuns=None, _clubHomePage=None, session=None):

        self.init_session(session)


        self.name = _name
        self.numberOfParkrunners = _numberOfParkrunners
        self.numberOfRuns = _numberOfRuns
        self.clubHomePage = _clubHomePage

        pass

    @classmethod
    def GetClubs(cls, event):

        cls.init_session()

        clubs = []

        clubsHTML = cls.session.get(event.url + "results/clublist/").text

        clubsSoup = BeautifulSoup(clubsHTML, "html.parser")
        clubRows = clubsSoup.find("table", {"id": "results"}).find("tbody").findAll("tr")
        
        for clubRow in clubRows:

            rowData = clubRow.findAll("td")

            club = Club(
                _name=rowData[0].find("a").text if rowData[0].find("a") else None,
                _numberOfParkrunners=rowData[1].text if rowData[1] else None,
                _numberOfRuns=rowData[2].text if rowData[2] else None,
                _clubHomePage=rowData[3].find("a")["href"] if rowData[3].find("a") else None,
            )

            clubs.append(club)

        return clubs

    @classmethod
    def GetLargestClubsGlobally(cls):

        cls.init_session()


        clubs = []

        clubsHTML = cls.session.get("https://www.parkrun.com/results/largestclubs/").text

        clubsSoup = BeautifulSoup(clubsHTML, "html.parser")
        clubRows = clubsSoup.find("table", {"id": "results"}).find("tbody").findAll("tr")
        
        for clubRow in clubRows:

            rowData = clubRow.findAll("td")

            club = Club(
                _name=rowData[0].text if rowData[0] else None,
                _numberOfParkrunners=rowData[1].text if rowData[1] else None,
                _numberOfRuns=rowData[2].text if rowData[2] else None,
                _clubHomePage=rowData[3].find("a")["href"] if rowData[3].find("a") else None,
            )

            clubs.append(club)

        return clubs

class Sub20Woman(BaseScraper):

    def __init__(self, _rank=None, _parkRunner=None, _numberOfRuns=None, _fastestTime=None, _club=None, session=None):

        self.init_session(session)


        self.rank = _rank
        self.parkRunner = _parkRunner
        self.numberOfRuns = _numberOfRuns
        self.fastestTime = _fastestTime
        self.club = _club

        pass

    @classmethod
    def GetSub20Women(cls, event):

        cls.init_session()


        sub20Women = []

        sub20WomenHTML = cls.session.get(event.url + "results/sub20women/").text

        sub20WomenSoup = BeautifulSoup(sub20WomenHTML, "html.parser")
        sub20WomenRows = sub20WomenSoup.find("table", {"id": "results"}).find("tbody").findAll("tr")
        
        for sub20WomenRow in sub20WomenRows:

            rowData = sub20WomenRow.findAll("td")

            sub20Woman = Sub20Woman(
                _rank=rowData[0].text if rowData[0] else None,
                _parkRunner=rowData[1].find("a").text if rowData[1].find("a") else None,
                _numberOfRuns=rowData[2].text if rowData[2] else None,
                _fastestTime=rowData[3].text if rowData[3] else None,
                _club=rowData[4].find("a").text if rowData[4].find("a") else None
            )

            sub20Women.append(sub20Woman)

        return sub20Women

class Sub17Man(BaseScraper):

    def __init__(self, _rank=None, _parkRunner=None, _numberOfRuns=None, _fastestTime=None, _club=None, session=None):

        self.init_session(session)


        self.rank = _rank
        self.parkRunner = _parkRunner
        self.numberOfRuns = _numberOfRuns
        self.fastestTime = _fastestTime
        self.club = _club

        pass

    @classmethod
    def GetSub17Men(cls, event):

        cls.init_session()

        sub17Men = []

        sub17MenHTML = cls.session.get(event.url + "results/sub17men/").text

        sub17MenSoup = BeautifulSoup(sub17MenHTML, "html.parser")
        sub17MenRows = sub17MenSoup.find("table", {"id": "results"}).find("tbody").findAll("tr")
        
        for sub17MenRow in sub17MenRows:

            rowData = sub17MenRow.findAll("td")

            sub17Man = Sub17Man(
                _rank=rowData[0].text,
                _parkRunner=rowData[1].find("a").text if rowData[1].find("a") else None,
                _numberOfRuns=rowData[2].text if rowData[2] else None,
                _fastestTime=rowData[3].text if rowData[3] else None,
                _club=rowData[4].find("a").text if rowData[4].find("a") else None,
            )

            sub17Men.append(sub17Man)

        return sub17Men

class AgeGradedLeagueRank(BaseScraper):

    def __init__(self, _rank=None, _parkRunner=None, _ageGrade=None, session=None):

        self.init_session(session)


        self.rank = _rank
        self.parkRunner = _parkRunner
        self.ageGrade = _ageGrade

        pass

    @classmethod
    def GetAgeGradedLeagueRanks(cls, event, quantity=1000):

        cls.init_session()

        ageGradedLeagueRanks = []

        resultSet = int(math.ceil(quantity/1000))

        for i in range(1, resultSet+1):

            # To avoid hammering server
            time.sleep(0.25)

            ageGradedLeagueRanksHTML = cls.session.get(event.url + f"results/agegradedleague/?resultSet={resultSet}").text

            ageGradedLeagueRanksSoup = BeautifulSoup(ageGradedLeagueRanksHTML, "html.parser")
            ageGradedLeagueRanksRows = ageGradedLeagueRanksSoup.find("table", {"id": "results"}).find("tbody").findAll("tr")
            
            for ageGradedLeagueRanksRow in ageGradedLeagueRanksRows:

                rowData = ageGradedLeagueRanksRow.findAll("td")

                ageGradedLeagueRank = AgeGradedLeagueRank(
                    _rank=rowData[0].text if rowData[0] else None,
                    _parkRunner=rowData[1].find("a").text if rowData[1].find("a") else None,
                    _ageGrade=rowData[2].text if rowData[2] else None
                )

                ageGradedLeagueRanks.append(ageGradedLeagueRank)

                if len(ageGradedLeagueRanks) == quantity:
                    return ageGradedLeagueRanks

        return ageGradedLeagueRanks

class Fastest(BaseScraper):

    def __init__(self, _rank=None, _parkRunner=None, _numberOfRuns=None, _sex=None, _fastestTime=None, _club=None, session=None):

        self.init_session(session)


        self.rank = _rank
        self.parkRunner = _parkRunner
        self.numberOfRuns = _numberOfRuns
        self.sex = _sex
        self.fastestTime = _fastestTime
        self.club = _club

        pass

    @classmethod
    def GetFastest500(cls, event):

        cls.init_session()

        fastest500 = []

        fastest500HTML = cls.session.get(event.url + "results/fastest500/").text

        fastest500Soup = BeautifulSoup(fastest500HTML, "html.parser")
        fastest500Rows = fastest500Soup.find("table", {"id": "results"}).find("tbody").findAll("tr")
        
        for fastest500Row in fastest500Rows:

            rowData = fastest500Row.findAll("td")

            fastest = Fastest(
                _rank=rowData[0].text if rowData[0] else None,
                _parkRunner=rowData[1].find("a").text if rowData[1].find("a") else None,
                _numberOfRuns=rowData[2].text if rowData[2] else None,
                _sex=rowData[3].text if rowData[3] else None,
                _fastestTime=rowData[4].text if rowData[4] else None,
                _club=rowData[5].find("a").text if rowData[5].find("a") else None,
            )

            fastest500.append(fastest)

        return fastest500

class WeekFirstFinisher(BaseScraper):

    def __init__(self, _event=None, _maleParkRunner=None, _maleClub=None, _femaleParkRunner=None, _femaleClub=None, session=None):

        self.init_session(session)


        self.event = _event
        self.maleParkRunner = _maleParkRunner
        self.maleClub = _maleClub
        self.femaleParkRunner = _femaleParkRunner
        self.femaleClub = _femaleClub

        pass

    @classmethod
    def GetWeekFirstFinishersForCountry(cls, country):

        cls.init_session()

        weekFirstFinishers = []

        weekFirstFinisherHTML = cls.session.get(country.url + "/results/firstfinishers/").text

        weekFirstFinisherSoup = BeautifulSoup(weekFirstFinisherHTML, "html.parser")
        weekFirstFinisherRows = weekFirstFinisherSoup.find("table", {"id": "results"}).find("tbody").findAll("tr")

        for weekFirstFinisherRow in weekFirstFinisherRows:

            rowData = weekFirstFinisherRow.findAll("td")

            weekFirstFinisher = WeekFirstFinisher(
                _event=rowData[0].find("a").text if rowData[0].find("a") else None,
                _maleParkRunner=rowData[2].find("a").text if rowData[2].find("a") else None,
                _maleClub=rowData[3].find("a").text if rowData[3].find("a") else None,
                _femaleParkRunner=rowData[5].find("a").text if rowData[5].find("a") else None,
                _femaleClub=rowData[6].find("a").text if rowData[6].find("a") else None,
            )

            weekFirstFinishers.append(weekFirstFinisher)

        return weekFirstFinishers

    @classmethod
    def GetWeekFirstFinishersGlobally(cls):

        cls.init_session()

        weekFirstFinishers = []

        weekFirstFinisherHTML = cls.session.get("https://www.parkrun.com/results/firstfinishers/").text

        weekFirstFinisherSoup = BeautifulSoup(weekFirstFinisherHTML, "html.parser")
        weekFirstFinisherRows = weekFirstFinisherSoup.find("table", {"id": "results"}).find("tbody").findAll("tr")

        for weekFirstFinisherRow in weekFirstFinisherRows:

            rowData = weekFirstFinisherRow.findAll("td")

            weekFirstFinisher = WeekFirstFinisher(
                _event=rowData[0].find("a").text if rowData[0].find("a") else None,
                _maleParkRunner=rowData[1].find("a").text if rowData[1].find("a") else None,
                _maleClub=rowData[2].text if rowData[2] else None,
                _femaleParkRunner=rowData[3].find("a").text if rowData[3].find("a") else None,
                _femaleClub=rowData[4].text if rowData[4] else None,
            )

            weekFirstFinishers.append(weekFirstFinisher)

        return weekFirstFinishers

class WeekSub17Run(BaseScraper):

    def __init__(self, _event=None, _parkRunner=None, _time=None, _club=None, session=None):

        self.init_session(session)


        self.event = _event
        self.parkRunner = _parkRunner
        self.time = _time
        self.club = _club

        pass

    @classmethod
    def GetWeekSub17RunsForCountry(cls, country):

        cls.init_session()

        weekSub17Runs = []

        weekSub17RunHTML = cls.session.get(country.url + "/results/sub17/").text

        weekSub17RunSoup = BeautifulSoup(weekSub17RunHTML, "html.parser")
        weekSub17RunRows = weekSub17RunSoup.find("table", {"id": "results"}).find("tbody").findAll("tr")

        for weekSub17RunRow in weekSub17RunRows:

            rowData = weekSub17RunRow.findAll("td")

            weekSub17Run = WeekSub17Run(
                _event=rowData[0].find("a").text if rowData[0].find("a") else None,
                _parkRunner=rowData[2].find("a").text if rowData[2].find("a") else None,
                _time=rowData[3].text if rowData[3] else None,
                _club=rowData[4].find("a").text if rowData[4].find("a") else None,
            )

            weekSub17Runs.append(weekSub17Run)

        return weekSub17Runs

    @classmethod
    def GetWeekSub17RunsGlobally(cls):

        cls.init_session()

        weekSub17Runs = []

        weekSub17RunHTML = cls.session.get("https://www.parkrun.com/results/sub17/").text

        weekSub17RunSoup = BeautifulSoup(weekSub17RunHTML, "html.parser")
        weekSub17RunRows = weekSub17RunSoup.find("table", {"id": "results"}).find("tbody").findAll("tr")

        for weekSub17RunRow in weekSub17RunRows:

            rowData = weekSub17RunRow.findAll("td")

            weekSub17Run = WeekSub17Run(
                _event=rowData[0].find("a").text if rowData[0].find("a") else None,
                _parkRunner=rowData[1].find("a").text if rowData[1].find("a") else None,
                _time=rowData[2].text if rowData[2] else None,
                _club=rowData[3].text if rowData[3] else None,
            )

            weekSub17Runs.append(weekSub17Run)

        return weekSub17Runs

class WeekTopAgeGrade(BaseScraper):

    def __init__(self, _event=None, _parkRunner=None, _time=None, _ageGroup=None, _ageGrade=None, _club=None, session=None):

        self.init_session(session)

        self.event = _event
        self.parkRunner = _parkRunner
        self.time = _time
        self.ageGroup = _ageGroup
        self.ageGrade = _ageGrade
        self.club = _club

        pass

    @classmethod
    def GetWeekTopAgeGradesForCountry(cls, country):

        cls.init_session()

        weekTopAgeGrades = []

        weekTopAgeGradeHTML = cls.session.get(country.url + "/results/topagegrade/").text

        weekTopAgeGradeSoup = BeautifulSoup(weekTopAgeGradeHTML, "html.parser")
        weekTopAgeGradeRows = weekTopAgeGradeSoup.find("table", {"id": "results"}).find("tbody").findAll("tr")

        for weekTopAgeGradeRow in weekTopAgeGradeRows:

            rowData = weekTopAgeGradeRow.findAll("td")

            weekTopAgeGrade = WeekTopAgeGrade(
                _event=rowData[0].find("a").text if rowData[0].find("a") else None,
                _parkRunner=rowData[2].find("a").text if rowData[2].find("a") else None,
                _time=rowData[3].text if rowData[3] else None,
                _ageGroup=rowData[4].text if rowData[4] else None,
                _ageGrade=rowData[5].text if rowData[5] else None,
                _club=rowData[6].find("a").text if rowData[6].find("a") else None,
            )

            weekTopAgeGrades.append(weekTopAgeGrade)

        return weekTopAgeGrades

    @classmethod
    def GetWeekTopAgeGradesGlobally(cls):

        cls.init_session()

        weekTopAgeGrades = []

        weekTopAgeGradeHTML = cls.session.get("https://www.parkrun.com/results/topagegrade/").text

        weekTopAgeGradeSoup = BeautifulSoup(weekTopAgeGradeHTML, "html.parser")
        weekTopAgeGradeRows = weekTopAgeGradeSoup.find("table", {"id": "results"}).find("tbody").findAll("tr")

        for weekTopAgeGradeRow in weekTopAgeGradeRows:

            rowData = weekTopAgeGradeRow.findAll("td")

            weekTopAgeGrade = WeekTopAgeGrade(
                _event=rowData[0].find("a").text if rowData[0].find("a") else None,
                _parkRunner=rowData[1].find("a").text if rowData[1].find("a") else None,
                _time=rowData[2].text if rowData[2] else None,
                _ageGroup=rowData[3].text if rowData[3] else None,
                _ageGrade=rowData[4].text if rowData[4] else None,
                _club=rowData[5].text if rowData[5] else None,
            )

            weekTopAgeGrades.append(weekTopAgeGrade)

        return weekTopAgeGrades

class WeekNewCategoryRecord(BaseScraper):

    def __init__(self, _event=None, _parkRunner=None, _time=None, _ageGroup=None, _ageGrade=None, _club=None, session=None):

        self.init_session(session)


        self.event = _event
        self.parkRunner = _parkRunner
        self.time = _time
        self.ageGroup = _ageGroup
        self.ageGrade = _ageGrade
        self.club = _club

        pass

    @classmethod
    def GetWeekNewCategoryRecordsForCountry(cls, country):

        cls.init_session()

        weekNewCategoryRecords = []

        weekNewCategoryRecordHTML = cls.session.get(country.url + "/results/newcategoryrecords/").text

        weekNewCategoryRecordSoup = BeautifulSoup(weekNewCategoryRecordHTML, "html.parser")
        weekNewCategoryRecordRows = weekNewCategoryRecordSoup.find("table", {"id": "results"}).find("tbody").findAll("tr")

        for weekNewCategoryRecordRow in weekNewCategoryRecordRows:

            rowData = weekNewCategoryRecordRow.findAll("td")

            weekNewCategoryRecord = WeekNewCategoryRecord(
                _event=rowData[0].find("a").text if rowData[0].find("a") else None,
                _parkRunner=rowData[2].find("a").text if rowData[2].find("a") else None,
                _time=rowData[3].text if rowData[3] else None,
                _ageGroup=rowData[4].text if rowData[4] else None,
                _ageGrade=rowData[5].text if rowData[5] else None,
                _club=rowData[6].find("a").text if rowData[6].find("a") else None
            )

            weekNewCategoryRecords.append(weekNewCategoryRecord)

        return weekNewCategoryRecords
        
    @classmethod
    def GetWeekNewCategoryRecordsGlobally(cls):

        cls.init_session()

        weekNewCategoryRecords = []

        weekNewCategoryRecordHTML = cls.session.get("https://www.parkrun.com/results/newcategoryrecords/").text

        weekNewCategoryRecordSoup = BeautifulSoup(weekNewCategoryRecordHTML, "html.parser")
        weekNewCategoryRecordRows = weekNewCategoryRecordSoup.find("table", {"id": "results"}).find("tbody").findAll("tr")

        for weekNewCategoryRecordRow in weekNewCategoryRecordRows:

            rowData = weekNewCategoryRecordRow.findAll("td")

            weekNewCategoryRecord = WeekNewCategoryRecord(
                _event=rowData[0].find("a").text if rowData[0].find("a") else None,
                _parkRunner=rowData[1].find("a").text if rowData[1].find("a") else None,
                _time=rowData[2].text if rowData[2] else None,
                _ageGroup=rowData[3].text if rowData[3] else None,
                _ageGrade=rowData[4].text if rowData[4] else None,
                _club=rowData[5].text if rowData[5] else None
            )

            weekNewCategoryRecords.append(weekNewCategoryRecord)

        return weekNewCategoryRecords

class CourseRecord(BaseScraper):

    def __init__(self, _event=None, _femaleParkRunner=None, _femaleTime=None, _femaleDate=None, _maleParkRunner=None, _maleTime=None, _maleDate=None, session=None):

        self.init_session(session)


        self.event = _event
        self.femaleParkRunner = _femaleParkRunner
        self.femaleTime = _femaleTime
        self.femaleDate = _femaleDate
        self.maleParkRunner = _maleParkRunner
        self.maleTime = _maleTime
        self.maleDate = _maleDate

        pass

    @classmethod
    def GetCourseRecordsForCountry(cls, country):

        cls.init_session()

        courseRecords = []

        courseRecordHTML = cls.session.get(country.url + "/results/courserecords/").text

        courseRecordSoup = BeautifulSoup(courseRecordHTML, "html.parser")
        courseRecordRows = courseRecordSoup.find("table", {"id": "results"}).find("tbody").findAll("tr")

        for courseRecordRow in courseRecordRows:

            rowData = courseRecordRow.findAll("td")

            courseRecord = CourseRecord(
                _event=rowData[0].find("a").text if rowData[0].find("a") else None,
                _femaleParkRunner=rowData[2].find("a").text if rowData[2].find("a") else None,
                _femaleTime=rowData[3].text if rowData[3] else None,
                _femaleDate=rowData[4].text if rowData[4] else None,
                _maleParkRunner=rowData[6].find("a").text if rowData[6].find("a") else None,
                _maleTime=rowData[7].text if rowData[7] else None,
                _maleDate=rowData[8].text if rowData[8] else None,
            )

            courseRecords.append(courseRecord)

        return courseRecords

    @classmethod
    def GetCourseRecordsGlobally(cls):

        cls.init_session()

        courseRecords = []

        courseRecordHTML = cls.session.get("https://www.parkrun.com/results/courserecords/").text

        courseRecordSoup = BeautifulSoup(courseRecordHTML, "html.parser")
        courseRecordRows = courseRecordSoup.find("table", {"id": "results"}).find("tbody").findAll("tr")

        for courseRecordRow in courseRecordRows:

            rowData = courseRecordRow.findAll("td")

            courseRecord = CourseRecord(
                _event=rowData[0].find("a").text if rowData[0].find("a") else None,
                _femaleParkRunner=rowData[1].find("a").text if rowData[1].find("a") else None,
                _femaleTime=rowData[2].text if rowData[2] else None,
                _femaleDate=rowData[3].text if rowData[3] else None,
                _maleParkRunner=rowData[4].find("a").text if rowData[4].find("a") else None,
                _maleTime=rowData[5].text if rowData[5] else None,
                _maleDate=rowData[6].text if rowData[6] else None,
            )

            courseRecords.append(courseRecord)

        return courseRecords

class AttendanceRecord(BaseScraper):

    def __init__(self, _event=None, _attendance=None, _week=None, _thisWeek=None, session=None):

        self.init_session(session)


        self.event = _event
        self.attendance = _attendance
        self.week = _week
        self.thisWeek = _thisWeek

        pass

    @classmethod
    def GetAttendanceRecordsForCountry(cls, country):

        cls.init_session()

        attendanceRecords = []

        attendanceRecordHTML = cls.session.get(country.url + "/results/attendancerecords/").text

        attendanceRecordSoup = BeautifulSoup(attendanceRecordHTML, "html.parser")
        attendanceRecordRows = attendanceRecordSoup.find("table", {"id": "results"}).find("tbody").findAll("tr")

        for attendanceRecordRow in attendanceRecordRows:

            rowData = attendanceRecordRow.findAll("td")

            attendanceRecord = AttendanceRecord(
                _event=rowData[0].find("a").text if rowData[0].find("a") else None,
                _attendance=rowData[2].text if rowData[2] else None,
                _week=rowData[3].text if rowData[3] else None,
                _thisWeek=rowData[4].text if rowData[4] else None,
            )

            attendanceRecords.append(attendanceRecord)

        return attendanceRecords

    @classmethod
    def GetAttendanceRecordsGlobally(cls):

        cls.init_session()

        attendanceRecords = []

        attendanceRecordHTML = cls.session.get("https://www.parkrun.com/results/attendancerecords/").text

        attendanceRecordSoup = BeautifulSoup(attendanceRecordHTML, "html.parser")
        attendanceRecordRows = attendanceRecordSoup.find("table", {"id": "results"}).find("tbody").findAll("tr")

        for attendanceRecordRow in attendanceRecordRows:

            rowData = attendanceRecordRow.findAll("td")

            attendanceRecord = AttendanceRecord(
                _event=rowData[0].find("a").text if rowData[0].find("a") else None,
                _attendance=rowData[1].text if rowData[1] else None,
                _week=rowData[2].text if rowData[2] else None,
                _thisWeek=rowData[3].text if rowData[3] else None,
            )

            attendanceRecords.append(attendanceRecord)

        return attendanceRecords

class MostEvent(BaseScraper):

    def __init__(self, _parkRunner=None, _events=None, _totalParkRuns=None, _totalParkRunsWorldwide=None, session=None):

        self.init_session(session)


        self.parkRunner = _parkRunner
        self.events = _events
        self.totalParkRuns = _totalParkRuns
        self.totalParkRunsWorldwide = _totalParkRunsWorldwide

        pass

    @classmethod
    def GetMostEventsForCountry(cls, country):

        cls.init_session()

        mostEvents = []

        mostEventHTML = cls.session.get(country.url + "/results/mostevents/").text

        mostEventSoup = BeautifulSoup(mostEventHTML, "html.parser")
        mostEventRows = mostEventSoup.find("table", {"id": "results"}).find("tbody").findAll("tr")

        for mostEventRow in mostEventRows:

            rowData = mostEventRow.findAll("td")

            mostEvent = MostEvent(
                _parkRunner=rowData[0].find("a").text if rowData[0].find("a") else None,
                _events=rowData[3].text if rowData[3] else None,
                _totalParkRuns=rowData[4].text if rowData[4] else None,
                _totalParkRunsWorldwide=rowData[5].text if rowData[5] else None,
            )

            mostEvents.append(mostEvent)

        return mostEvents

    @classmethod
    def GetMostEventsGlobally(cls):

        cls.init_session()

        mostEvents = []

        mostEventHTML = cls.session.get("https://www.parkrun.com/results/mostevents/").text

        mostEventSoup = BeautifulSoup(mostEventHTML, "html.parser")
        mostEventRows = mostEventSoup.find("table", {"id": "results"}).find("tbody").findAll("tr")

        for mostEventRow in mostEventRows:

            rowData = mostEventRow.findAll("td")

            mostEvent = MostEvent(
                _parkRunner=rowData[0].find("a").text if rowData[0].find("a") else None,
                _events=rowData[2].text if rowData[2] else None,
                _totalParkRuns=rowData[3].text if rowData[3] else None,
            )

            mostEvents.append(mostEvent)

        return mostEvents

class LargestClub(BaseScraper):

    def __init__(self, _club=None, _numberOfParkRunners=None, _numberOfRuns=None, _clubHomePage=None, session=None):

        self.init_session(session)

        self.club = _club
        self.numberOfParkRunners = _numberOfParkRunners
        self.numberOfRuns = _numberOfRuns
        self.clubHomePage = _clubHomePage

        pass

    @classmethod
    def GetLargestClubsForCountry(cls, country):

        cls.init_session()

        largestClubs = []

        largestClubHTML = cls.session.get(country.url + "/results/largestclubs/").text

        largestClubSoup = BeautifulSoup(largestClubHTML, "html.parser")
        largestClubRows = largestClubSoup.find("table", {"id": "results"}).find("tbody").findAll("tr")

        for largestClubRow in largestClubRows:

            rowData = largestClubRow.findAll("td")

            largestClub = LargestClub(
                _club=rowData[0].find("a").text if rowData[0].find("a") else None,
                _numberOfParkRunners=rowData[2].text if rowData[2] else None,
                _numberOfRuns=rowData[3].text if rowData[3] else None,
                _clubHomePage=rowData[4].find("a")["href"] if rowData[4].find("a") else None,
            )

            largestClubs.append(largestClub)

        return largestClubs

class Joined100Club(BaseScraper):

    def __init__(self, _parkRunner=None, _numberOfRuns=None, session=None):

        self.init_session(session)

        self.parkRunner = _parkRunner
        self.numberOfRuns = _numberOfRuns

        pass

    @classmethod
    def GetJoined100ClubsForCountry(cls, country):

        cls.init_session()

        joined100Clubs = []

        joined100ClubHTML = cls.session.get(country.url + "/results/100clubbers/").text

        joined100ClubSoup = BeautifulSoup(joined100ClubHTML, "html.parser")
        joined100ClubRows = joined100ClubSoup.find("table", {"id": "results"}).find("tbody").findAll("tr")

        for joined100ClubRow in joined100ClubRows:

            rowData = joined100ClubRow.findAll("td")

            joined100Club = Joined100Club(
                _parkRunner=rowData[0].find("a").text if rowData[0].find("a") else None,
                _numberOfRuns="100" if rowData[1].find("img") else rowData[1].text,
            )

            joined100Clubs.append(joined100Club)

        return joined100Clubs

class MostFirstFinish(BaseScraper):

    def __init__(self, _parkRunner=None, _numberOfRuns=None, session=None):

        self.init_session(session)


        self.parkRunner = _parkRunner
        self.numberOfRuns = _numberOfRuns

        pass

    @classmethod
    def GetMostFirstFinishesForCountry(cls, country):

        cls.init_session()

        mostFirstFinishes = []

        mostFirstFinishHTML = cls.session.get(country.url + "/results/mostfirstfinishes/").text

        mostFirstFinishSoup = BeautifulSoup(mostFirstFinishHTML, "html.parser")
        mostFirstFinishRows = mostFirstFinishSoup.find("table", {"id": "results"}).find("tbody").findAll("tr")

        for mostFirstFinishRow in mostFirstFinishRows:

            rowData = mostFirstFinishRow.findAll("td")

            mostFirstFinish = MostFirstFinish(
                _parkRunner=rowData[0].find("a").text if rowData[0].find("a") else None,
                _numberOfRuns=rowData[1].text if rowData[1] else None,
            )

            mostFirstFinishes.append(mostFirstFinish)

        return mostFirstFinishes

    @classmethod
    def GetMostFirstFinishesGlobally(cls):

        cls.init_session()

        mostFirstFinishes = []

        mostFirstFinishHTML = cls.session.get("https://www.parkrun.com/results/mostfirstfinishes/").text

        mostFirstFinishSoup = BeautifulSoup(mostFirstFinishHTML, "html.parser")
        mostFirstFinishRows = mostFirstFinishSoup.find("table", {"id": "results"}).find("tbody").findAll("tr")

        for mostFirstFinishRow in mostFirstFinishRows:

            rowData = mostFirstFinishRow.findAll("td")

            mostFirstFinish = MostFirstFinish(
                _parkRunner=rowData[0].find("a").text if rowData[0].find("a") else None,
                _numberOfRuns=rowData[1].text if rowData[1] else None,
            )

            mostFirstFinishes.append(mostFirstFinish)

        return mostFirstFinishes

class FreedomRun(BaseScraper):

    def __init__(self, _parkRunner=None, _date=None, _location=None, _runTime=None, session=None):

        self.init_session(session)


        self.parkRunner = _parkRunner
        self.date = _date
        self.location = _location
        self.runTime = _runTime

        pass

    @classmethod
    def GetFreedomRunsForCountry(cls, country):

        cls.init_session()

        freedomRuns = []

        freedomRunHTML = cls.session.get(country.url + "/results/freedom/").text

        freedomRunSoup = BeautifulSoup(freedomRunHTML, "html.parser")
        freedomRunRows = freedomRunSoup.find("table", {"id": "results"}).find("tbody").findAll("tr")

        for freedomRunRow in freedomRunRows:

            rowData = freedomRunRow.findAll("td")

            freedomRun = FreedomRun(
                _parkRunner=rowData[0].find("a").text if rowData[0].find("a") else None,
                _date=rowData[1].text if rowData[1] else None,
                _location=rowData[2].text if rowData[2] else None,
                _runTime=rowData[3].text if rowData[3] else None,
            )

            freedomRuns.append(freedomRun)

        return freedomRuns

    @classmethod
    def GetFreedomRunsGlobally(cls):

        cls.init_session()

        freedomRuns = []

        freedomRunHTML = cls.session.get("https://www.parkrun.com/results/freedom/").text

        freedomRunSoup = BeautifulSoup(freedomRunHTML, "html.parser")
        freedomRunRows = freedomRunSoup.find("table", {"id": "results"}).find("tbody").findAll("tr")

        for freedomRunRow in freedomRunRows:

            rowData = freedomRunRow.findAll("td")

            freedomRun = FreedomRun(
                _parkRunner=rowData[0].find("a").text if rowData[0].find("a") else None,
                _date=rowData[1].text if rowData[1] else None,
                _location=rowData[2].text if rowData[2] else None,
                _runTime=rowData[3].text if rowData[3] else None,
            )

            freedomRuns.append(freedomRun)

        return freedomRuns

class HistoricNumber(BaseScraper):

    session = None

    def __init__(self, _date=None, _events=None, _athletes=None, _volunteers=None, session=None):

        self.init_session(session)

        self.date = _date
        self.events = _events
        self.athletes = _athletes
        self.volunteers = _volunteers

        pass

    @classmethod
    def GetHistoricNumbersForCountry(cls, country=None):

        cls.init_session()

        historicNumbers = []
        historicNumberHTML = None

        if country:

            historicNumberHTML = cls.session.get("https://results-service.parkrun.com/resultsSystem/App/globalChartNumRunnersAndEvents.php?CountryNum=" + country.id).text

        else:

            historicNumberHTML = cls.session.get("https://results-service.parkrun.com/resultsSystem/App/globalChartNumRunnersAndEvents.php").text

        searchString = "data.addRows(["
        contentStartIndex = historicNumberHTML.find(searchString) + len(searchString)
        contentEndIndex = historicNumberHTML.find("]);", contentStartIndex)
        contentString = historicNumberHTML[contentStartIndex:contentEndIndex].replace("\n","").replace("\r","").replace("\t","").replace(" ","")

        contentList = contentString.split("],")

        for contentRow in contentList:

            if contentRow.strip() == "":

                continue

            splitContentRow = contentRow.split(",")
            dateStart = splitContentRow[0].find("(")
            dateEnd = splitContentRow[0].find(")")
            date = splitContentRow[0][dateStart + 1:dateEnd].replace("\"","")

            historicNumber = HistoricNumber(
                _date=date,
                _events=splitContentRow[1],
                _athletes=splitContentRow[2],
                _volunteers=splitContentRow[3],
            )

            historicNumbers.append(historicNumber)

        return historicNumbers
        