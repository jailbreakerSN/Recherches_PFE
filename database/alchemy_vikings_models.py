# coding: utf-8
from sqlalchemy import BIGINT, Column, Date, ForeignKey, INTEGER, String, Table, Text, text
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.mysql.types import TINYINT
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()
metadata = Base.metadata


class EstCreeUser(Base):
    __tablename__ = 'est_cree_user'

    id_Utilisateur = Column(ForeignKey('utilisateur.id_Utilisateur'), primary_key=True, nullable=False, server_default=text("'0'"))
    id_Projet = Column(ForeignKey('projet.id_Projet'), primary_key=True, nullable=False, index=True, server_default=text("'0'"))
    date_creation_est_Cree_User = Column(Date)

    projet = relationship('Projet')
    utilisateur = relationship('Utilisateur')


t_est_mene_user = Table(
    'est_mene_user', metadata,
    Column('id_Projet', ForeignKey('projet.id_Projet'), primary_key=True, nullable=False, server_default=text("'0'")),
    Column('id_Utilisateur', ForeignKey('utilisateur.id_Utilisateur'), primary_key=True, nullable=False, index=True, server_default=text("'0'"))
)


class Etape(Base):
    __tablename__ = 'etape'

    id_Etape = Column(BIGINT(20), primary_key=True)
    nom = Column(String(30))
    objectif = Column(String(255))
    importance = Column(INTEGER(11))
    valide_Etape = Column(TINYINT(1))
    version_Etape = Column(String(30))
    id_Langage = Column(ForeignKey('langage.id_Langage'), index=True)
    id_Workflow = Column(ForeignKey('workflow.id_Workflow'), index=True)

    langage = relationship('Langage')
    workflow = relationship('Workflow')


class Langage(Base):
    __tablename__ = 'langage'

    id_Langage = Column(BIGINT(20), primary_key=True)
    nom = Column(String(30))


class Projet(Base):
    __tablename__ = 'projet'

    id_Projet = Column(BIGINT(20), primary_key=True)
    nom = Column(String(30))
    description_Projet = Column(Text)
    workflow_id_workflow = Column(ForeignKey('workflow.id_Workflow'), index=True)

    workflow = relationship('Workflow', primaryjoin='Projet.workflow_id_workflow == Workflow.id_Workflow')
    utilisateur = relationship('Utilisateur', secondary='est_mene_user')


class Utilisateur(Base):
    __tablename__ = 'utilisateur'

    id_Utilisateur = Column(BIGINT(20), primary_key=True)
    username_Utilisateur = Column(String(30))
    email_Utilisateur = Column(String(42))
    firstname_Utilisateur = Column(String(30))
    lastname_Utilisateur = Column(String(30))
    password_Utilisateur = Column(String(255))


class VariableEnv(Base):
    __tablename__ = 'variable_env'

    id_Variable_Env = Column(BIGINT(20), primary_key=True)
    libelle_Variable_Env = Column(String(30))
    valeur_Variable_Env = Column(String(255))
    id_Etape = Column(ForeignKey('etape.id_Etape'), index=True)

    etape = relationship('Etape')


class Workflow(Base):
    __tablename__ = 'workflow'

    id_Workflow = Column(BIGINT(20), primary_key=True)
    nom = Column(String(30))
    description = Column(Text)
    projet_id_projet = Column(ForeignKey('projet.id_Projet'), index=True)

    projet = relationship('Projet', primaryjoin='Workflow.projet_id_projet == Projet.id_Projet')
