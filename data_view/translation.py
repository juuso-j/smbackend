from modeltranslation.translator import TranslationOptions, translator


from data_view.models import (
    MobileUnitGroup,
    MobileUnit,
)


class MobileUnitGroupTranslationOptions(TranslationOptions):
    fields = ("name", "description")

translator.register(MobileUnitGroup, MobileUnitGroupTranslationOptions)


class MobileUnitTranslationOptions(TranslationOptions):
    fields = ("name","address")
translator.register(MobileUnit, MobileUnitTranslationOptions)