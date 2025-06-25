import api.database.models as models
from api.database import SessionLocal
from exceptions.api.database import DatabaseException, NotFoundException

class TemplateRepository:

    @classmethod
    def get_templates(cls):
        session = SessionLocal()
        try:
            templates = session.query(models.Template).all()  # Replace with your actual query
            return templates
        except Exception as e:
            # Handle session creation error (e.g., database connection issue)
            raise DatabaseException(f"Error trying to get templates. Database connection error: '{str(e)}'")
        finally:
            session.close()

    # @classmethod
    # def get_workflows(cls):
    #     session = SessionLocal()
    #     try:
    #         workflows = session.query(models.Workflow).all() 
    #         return workflows
    #     except Exception as e:
    #         # Handle session creation error (e.g., database connection issue)
    #         raise DatabaseException(f"Error trying to get workflows. Database connection error: {str(e)}")
    #     finally:
    #         session.close()

    @classmethod
    def get_template(cls, template: str):
        session = SessionLocal()
        try:
            template_object = session.query(models.Template).filter(models.Template.name == template).first()
            if template_object:
                return template_object
            else:
                raise NotFoundException(f"Error trying to get template: '{template}'. Template '{template}' does not exist!")
        except NotFoundException as e:
            # Handle not found error specifically
            raise e
        except Exception as e:
            # Handle session creation error (e.g., database connection issue)
            raise DatabaseException(f"Error trying to get template: '{template}'. Database connection error: '{str(e)}'")
        finally:
            session.close()

    @classmethod
    def set_template_description(cls, template: str, description: str):
        session = SessionLocal()
        try:
            template_object = session.query(models.Template).filter(models.Template.name == template).first()
            if template_object:
                template_object.description = description
                session.commit()
                return 
            else:
                raise NotFoundException(f"Error trying to set template description for template: '{template}'. Templates '{template}' does not exist!")
        except NotFoundException as e:
            session.rollback()
            raise e
        except Exception as e:
            session.rollback()
            raise DatabaseException(f"Error trying to set template description for template: '{template}'. Database connection error: '{str(e)}'")
        finally:
            session.close()
    
    @classmethod
    def delete_template_description(cls, template: str):
        session = SessionLocal()
        try:
            template_object = session.query(models.Template).filter(models.Template.name == template).first()
            if template_object:
                template_object.description = None
                session.commit()
                return
            else:
                raise NotFoundException(f"Error trying to delete template description for template: '{template}'. Template does not exist!")
        except NotFoundException as e:
            session.rollback()
            raise e
        except Exception as e:
            session.rollback()
            raise DatabaseException(f"Error trying to delete template description for template: '{template}'. Database connection error: '{str(e)}'")
        finally:
            session.close()