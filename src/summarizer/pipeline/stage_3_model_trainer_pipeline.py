from src.summarizer.config.configuration import ConfigurationManager
from src.summarizer.components.model_trainer import ModelTrainer
from src.summarizer.logging import logger


class ModelTrainerTrainingPipeline:
    def __init__(self):
        pass

    def initiate_model_trainer(self):
        try:
            logger.info(">>>>>> Stage: Model Trainer Stage started <<<<<<")
            
            config_manager = ConfigurationManager()
            model_trainer_config = config_manager.get_model_trainer_config()
            data_transformation_config = config_manager.get_data_transformation_config()

            train_path = data_transformation_config.train_path
            eval_path = data_transformation_config.test_path

            model_trainer = ModelTrainer(config=model_trainer_config)
            model_trainer.train(train_path=train_path, eval_path=eval_path)

            logger.info("✅ Model training completed successfully.")
        except Exception as e:
            logger.exception(f"Error in Model Trainer Stage: {e}")
            raise e
