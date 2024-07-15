from sqlalchemy import select
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from fastapi import HTTPException
import logging
from models import TeachersInstruments, Instrument, Teacher

# Encontar una relación profesor-instrumento
def get_teacher_instruments(db: Session, teachers_instruments_id: int):
    try:
        stmt = select(TeachersInstruments).where(TeachersInstruments.id == teachers_instruments_id)
        result = db.scalars(stmt).first()
        
        if result is None:
            raise HTTPException(status_code=404, detail="Relación de profesor-instumentos no encontrada")
        
        return result

    except SQLAlchemyError as e:
        logging.error(f"Error de base de datos al obtener instrumentos de profesor: {str(e)}")
        raise HTTPException(status_code=500, detail="Error en la base de datos")
    
    except Exception as e:
        logging.error(f"Error inesperado al obtener instrumentos de profesor: {str(e)}")
        raise HTTPException(status_code=500, detail="Error inesperado")

# Listar todas las relaciones de profesor-instrumento
def get_teachers_instruments(db: Session):
    try:
        stmt = select(TeachersInstruments)
        instruments = db.scalars(stmt).all()
        return instruments
    except SQLAlchemyError as e:
        logging.error(f"Error de base de datos al obtener instrumentos de profesores: {str(e)}")
        raise HTTPException(status_code=500, detail="Error en la base de datos")
    except Exception as e:
        logging.error(f"Error inesperado al obtener instrumentos de profesores: {str(e)}")
        raise HTTPException(status_code=500, detail="Error inesperado")

# Crear una nueva relación profesor-instrumento
def create_teachers_instruments(db: Session, teacher_id: int, instrument_id: int):
    try:
        # Verificar si el profesor existe
        teacher = db.get(Teacher, teacher_id)
        if not teacher:
            raise HTTPException(status_code=404, detail="Profesor no encontrado")

        # Verificar si el instrumento existe
        instrument = db.get(Instrument, instrument_id)
        if not instrument:
            raise HTTPException(status_code=404, detail="Instrumento no encontrado")

        # Verificar si ya existe la relación profesor-instrumento
        stmt = select(TeachersInstruments).where(
            (TeachersInstruments.instrument_id == instrument_id) &
            (TeachersInstruments.teacher_id == teacher_id)
        )
        result = db.execute(stmt).scalars().first()
        if result:
            raise HTTPException(status_code=400, detail="La relación profesor-instrumento ya existe")

        # Crear una nueva relación
        new_teachers_instruments = TeachersInstruments(
            teacher_id=teacher_id,
            instrument_id=instrument_id
        )
        db.add(new_teachers_instruments)
        db.commit()
        db.refresh(new_teachers_instruments)  # Refrescar la instancia para obtener los datos actualizados
        return new_teachers_instruments

    except SQLAlchemyError as e:
        db.rollback()
        logging.error(f"Error de base de datos al crear relación profesor-instrumento: {str(e)}")
        raise HTTPException(status_code=500, detail="Error en la base de datos")
    
    except Exception as e:
        db.rollback()
        logging.error(f"Error inesperado al crear relación profesor-instrumento: {str(e)}")
        raise HTTPException(status_code=500, detail="Error inesperado")

def update_teachers_instruments(db: Session, teachers_instruments_id: int, **kwargs):
    try:
        # Verificar si la relación existe
        teachers_instruments = db.get(TeachersInstruments, teachers_instruments_id)
        if not teachers_instruments:
            raise HTTPException(status_code=404, detail="Relación profesor-instrumento no encontrada")

        # Verificar si el profesor existe 
        if 'teacher_id' in kwargs:
            teacher = db.get(Teacher, kwargs['teacher_id'])
            if not teacher:
                raise HTTPException(status_code=404, detail="Profesor no encontrado")

        # Verificar si el instrumento existe 
        if 'instrument_id' in kwargs:
            instrument = db.get(Instrument, kwargs['instrument_id'])
            if not instrument:
                raise HTTPException(status_code=404, detail="Instrumento no encontrado")

        # Actualizar los campos de la relación
        for key, value in kwargs.items():
            if hasattr(teachers_instruments, key):
                setattr(teachers_instruments, key, value)

        db.commit()
        db.refresh(teachers_instruments)  # Refrescar la instancia para obtener los datos actualizados
        return teachers_instruments

    except SQLAlchemyError as e:
        db.rollback()
        logging.error(f"Error de base de datos al actualizar relación profesor-instrumento: {str(e)}")
        raise HTTPException(status_code=500, detail="Error en la base de datos")

    except Exception as e:
        db.rollback()
        logging.error(f"Error inesperado al actualizar relación profesor-instrumento: {str(e)}")
        raise HTTPException(status_code=500, detail="Error inesperado")

def delete_teacher_instruments(db: Session, teacher_instrument_id: int) -> bool:
    # Verificar si la relación existe
    teachers_instruments = db.get(TeachersInstruments, teacher_instrument_id)
    if not teachers_instruments:
        raise HTTPException(status_code=404, detail="Relación profesor-instrumento no encontrada")

    # Intentar eliminar la relación
    try:
        db.delete(teachers_instruments)
        db.commit()
        return True
    except SQLAlchemyError as e:
        db.rollback()
        logging.error(f"Error de base de datos al eliminar relación profesor-instrumento: {str(e)}")
        raise HTTPException(status_code=500, detail="Error en la base de datos")
    except Exception as e:
        db.rollback()
        logging.error(f"Error inesperado al eliminar relación profesor-instrumento: {str(e)}")
        raise HTTPException(status_code=500, detail="Error inesperado")