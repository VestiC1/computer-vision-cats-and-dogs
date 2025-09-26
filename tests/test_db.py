#!/usr/bin/env python3
"""Tests pytest de la base de données PostgreSQL"""
import pytest
from sqlmodel import Session, text
from pathlib import Path
import sys

# Configuration
ROOT_DIR = Path(__file__).parent.parent
sys.path.insert(0, str(ROOT_DIR))
from src.database.crud import engine

class TestDatabaseConnection:
    """Tests de connexion et de structure de la base de données"""

    def test_connection(self):
        """Teste la connexion à la base de données"""
        with Session(engine) as session:
            result = session.execute(text("SELECT 1"))
            assert result.scalar() == 1

    def test_tables_exist(self):
        """Vérifie que les tables nécessaires existent"""
        with Session(engine) as session:
            tables = session.execute(
                text("""
                    SELECT table_name
                    FROM information_schema.tables
                    WHERE table_schema = 'public'
                """)
            ).fetchall()

            table_names = [table[0] for table in tables]
            assert "feedback" in table_names, "Table 'feedback' introuvable"
            assert "monitoring" in table_names, "Table 'monitoring' introuvable"

    def test_feedback_table_structure(self):
        """Vérifie la structure de la table feedback"""
        with Session(engine) as session:
            feedback_columns = session.execute(
                text("""
                    SELECT column_name
                    FROM information_schema.columns
                    WHERE table_name = 'feedback'
                """)
            ).fetchall()

            feedback_columns = [col[0] for col in feedback_columns]
            expected_columns = ["id", "feed_back_value", "prob_cat", "prob_dog", "last_modified"]

            for col in expected_columns:
                assert col in feedback_columns, f"Colonne '{col}' manquante dans 'feedback'"

    def test_monitoring_table_structure(self):
        """Vérifie la structure de la table monitoring"""
        with Session(engine) as session:
            monitoring_columns = session.execute(
                text("""
                    SELECT column_name
                    FROM information_schema.columns
                    WHERE table_name = 'monitoring'
                """)
            ).fetchall()

            monitoring_columns = [col[0] for col in monitoring_columns]
            expected_columns = ["id", "timestamp", "inference_time", "succes", "feedback_id"]

            for col in expected_columns:
                assert col in monitoring_columns, f"Colonne '{col}' manquante dans 'monitoring'"

    def test_foreign_key_relation(self):
        """Vérifie la relation de clé étrangère entre monitoring et feedback"""
        with Session(engine) as session:
            foreign_keys = session.execute(
                text("""
                    SELECT conname
                    FROM pg_constraint
                    WHERE conrelid = 'monitoring'::regclass
                    AND contype = 'f'
                """)
            ).fetchall()
            assert len(foreign_keys) > 0, "Clé étrangère manquante entre 'monitoring' et 'feedback'"

    def test_column_types(self):
        """Vérifie les types des colonnes (optionnel)"""
        with Session(engine) as session:
            # Vérifie que feed_back_value est un integer
            column_type = session.execute(
                text("""
                    SELECT data_type
                    FROM information_schema.columns
                    WHERE table_name = 'feedback' AND column_name = 'feed_back_value'
                """)
            ).scalar()
            assert column_type == 'integer', "feed_back_value devrait être de type integer"

            # Vérifie que prob_cat et prob_dog sont des double precision (float)
            for column in ['prob_cat', 'prob_dog']:
                column_type = session.execute(
                    text(f"""
                        SELECT data_type
                        FROM information_schema.columns
                        WHERE table_name = 'feedback' AND column_name = '{column}'
                    """)
                ).scalar()
                assert column_type in ['double precision', 'real'], f"{column} devrait être de type float"

if __name__ == "__main__":
    # Permet l'exécution directe du fichier avec pytest
    pytest.main([__file__, "-v"])
