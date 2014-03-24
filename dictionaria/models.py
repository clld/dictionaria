from zope.interface import implementer
from sqlalchemy import (
    Column,
    String,
    Unicode,
    Integer,
    Boolean,
    ForeignKey,
    UniqueConstraint,
    Date,
)
from sqlalchemy.orm import relationship, backref
from sqlalchemy.ext.declarative import declared_attr
from sqlalchemy.ext.hybrid import hybrid_property

from clld import interfaces
from clld.db.meta import Base, CustomModelMixin
from clld.db.models import common

from dictionaria.interfaces import ISemanticField


@implementer(ISemanticField)
class SemanticField(Base, common.IdNameDescriptionMixin):
    pass


#-----------------------------------------------------------------------------
# specialized common mapper classes
#-----------------------------------------------------------------------------
@implementer(interfaces.IContribution)
class Dictionary(common.Contribution, CustomModelMixin):
    """Contributions in WOW are dictionaries which are always related to one language.
    """
    pk = Column(Integer, ForeignKey('contribution.pk'), primary_key=True)
    language_pk = Column(Integer, ForeignKey('language.pk'))
    language = relationship('Language', backref='dictionaries')
    published = Column(Date)


@implementer(interfaces.IParameter)
class Meaning(common.Parameter, CustomModelMixin):
    pk = Column(Integer, ForeignKey('parameter.pk'), primary_key=True)

    semantic_field_pk = Column(Integer, ForeignKey('semanticfield.pk'))
    semantic_field = relationship(SemanticField, backref='meanings')

    semantic_category = Column(Unicode)

    ids_code = Column(String)
    representation = Column(Integer)


@implementer(interfaces.IUnit)
class Word(common.Unit, CustomModelMixin):
    """Words are units of a particular language, but are still considered part of a
    dictionary, i.e. part of a contribution.
    """
    pk = Column(Integer, ForeignKey('unit.pk'), primary_key=True)
    phonetic = Column(Unicode)
    #script = Column(Unicode)
    #borrowed = Column(Unicode)

    # the concatenated values for the UnitParameter part of speech is stored denormalized.
    pos = Column(Unicode)

    dictionary_pk = Column(Integer, ForeignKey('dictionary.pk'))
    dictionary = relationship(Dictionary, backref='words')
    number = Column(Integer, default=0)  # for diambiguation of words with the same name

    @property
    def linked_from(self):
        return [w.source for w in self.source_assocs]

    @property
    def links_to(self):
        return [w.target for w in self.target_assocs]


class SeeAlso(Base):
    source_pk = Column(Integer, ForeignKey('word.pk'))
    target_pk = Column(Integer, ForeignKey('word.pk'))
    description = Column(Unicode())

    source = relationship(Word, foreign_keys=[source_pk], backref='target_assocs')
    target = relationship(Word, foreign_keys=[target_pk], backref='source_assocs')


class WordSentence(Base):
    word_pk = Column(Integer, ForeignKey('word.pk'))
    sentence_pk = Column(Integer, ForeignKey('sentence.pk'))
    description = Column(Unicode())

    word = relationship(Word, backref='sentence_assocs')
    sentence = relationship(
        common.Sentence, backref='word_assocs', order_by=common.Sentence.id)


@implementer(interfaces.IValue)
class Counterpart(common.Value, CustomModelMixin):
    """Counterparts relate a word to a meaning, i.e. they are the values for meaning
    parameters.
    """
    pk = Column(Integer, ForeignKey('value.pk'), primary_key=True)

    word_pk = Column(Integer, ForeignKey('word.pk'))
    word = relationship(Word, backref='counterparts')