import datetime

from pydantic import BaseModel, ConfigDict

variables_type = int | float | str

phone_number_pattern = r"^7\d{1,14}$"


class AdditionalModel(BaseModel):
    fullListMethod: str = "reject"
    fullListTime: int = 0
    useTr: bool = True
    allowCallTimeFrom: str = "32401"
    allowCallTimeTo: str = "75599"
    recordCall: bool = True
    recTrimLeft: int = 0
    detectRobot: bool = False
    providerId: int | None = None


class RedialCountOptions(BaseModel):
    redial: bool
    count: int


class RedialCountTimeOptions(RedialCountOptions):
    time: int


class RedialStrategy(BaseModel):
    redialStrategyEn: bool = False
    # busy: RedialCountTimeOptions = RedialCountTimeOptions(redial=True, count=3, time=3600)
    # noAnswer: RedialCountTimeOptions = RedialCountTimeOptions(redial=True, count=3, time=3600)
    # answerMash: RedialCountTimeOptions = RedialCountTimeOptions(redial=False, count=1, time=1)
    # congestion: RedialCountTimeOptions = RedialCountTimeOptions(redial=False, count=1, time=1)
    # answerNoList: RedialCountTimeOptions = RedialCountTimeOptions(redial=True, count=3, time=3600)


class CreateCallModel(BaseModel):
    name: str = f"Test call {datetime.datetime.now()}"
    defaultExec: str = "robot"
    secondExec: str = "ignore"
    defaultExecData: str = "2ecf569d-cb72-40a3-afc6-6f0544f4a4fc"
    cidType: str = "gornum"
    cidData: str = "92fc4374-0bd7-40ec-bc7b-28bebbdf53c7"
    startType: str = "manual"
    cps: float = 0.4
    webhookUrls: list[str] = []
    additionalOptions: AdditionalModel = AdditionalModel()
    redialStrategyOptions: RedialStrategy = RedialStrategy()


class Variables(BaseModel):
    model_config = ConfigDict(extra="allow")

    line_phone: str | None = None


class Contact(BaseModel):
    phone: list[str]
    variables: Variables | None = None
    autoCallId: str | None = None


class SendContacts(BaseModel):
    forceStart: bool = True
    batch: list[Contact] | None = None
