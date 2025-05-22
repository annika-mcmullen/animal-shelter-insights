# src/inspect_database.py
import sqlite3
import pandas as pd
import os
from datetime import datetime


def inspect_database(db_path="data/shelter_data.db"):
    """Inspect the shelter database and show summary statistics"""

    if not os.path.exists(db_path):
        print(f"Database not found at {db_path}")
        return

    conn = sqlite3.connect(db_path)

    try:
        print("🔍 DATABASE INSPECTION REPORT")
        print("=" * 50)

        # Check if tables exist
        tables_query = "SELECT name FROM sqlite_master WHERE type='table';"
        tables = pd.read_sql_query(tables_query, conn)
        print(f"\nTables in database: {list(tables['name'])}")

        # Animals table inspection
        if 'animals' in tables['name'].values:
            print(f"\nANIMALS TABLE")
            print("-" * 30)

            # Count total animals
            count_query = "SELECT COUNT(*) as total FROM animals;"
            total_animals = pd.read_sql_query(count_query, conn)['total'][0]
            print(f"Total animals: {total_animals}")

            if total_animals > 0:
                # Species breakdown
                species_query = "SELECT species, COUNT(*) as count FROM animals GROUP BY species ORDER BY count DESC;"
                species_data = pd.read_sql_query(species_query, conn)
                print(f"\nSpecies breakdown:")
                for _, row in species_data.iterrows():
                    print(f"  {row['species']}: {row['count']}")

                # Status breakdown
                status_query = "SELECT status, COUNT(*) as count FROM animals GROUP BY status ORDER BY count DESC;"
                status_data = pd.read_sql_query(status_query, conn)
                print(f"\nStatus breakdown:")
                for _, row in status_data.iterrows():
                    print(f"  {row['status']}: {row['count']}")

                # Age breakdown
                age_query = "SELECT age, COUNT(*) as count FROM animals WHERE age IS NOT NULL GROUP BY age ORDER BY count DESC;"
                age_data = pd.read_sql_query(age_query, conn)
                print(f"\nAge breakdown:")
                for _, row in age_data.iterrows():
                    print(f"  {row['age']}: {row['count']}")

                # Size breakdown (for dogs mainly)
                size_query = "SELECT size, COUNT(*) as count FROM animals WHERE size IS NOT NULL GROUP BY size ORDER BY count DESC;"
                size_data = pd.read_sql_query(size_query, conn)
                print(f"\nSize breakdown:")
                for _, row in size_data.iterrows():
                    print(f"  {row['size']}: {row['count']}")

                # Recent additions
                recent_query = """
                SELECT name, species, breed_primary, age, scraped_at 
                FROM animals 
                ORDER BY scraped_at DESC 
                LIMIT 5;
                """
                recent_animals = pd.read_sql_query(recent_query, conn)
                print(f"\nMost recently added animals:")
                for _, row in recent_animals.iterrows():
                    print(f"  {row['name']} ({row['species']}) - {row['breed_primary']} - {row['age']}")

        # Organizations table inspection
        if 'organizations' in tables['name'].values:
            print(f"\nORGANIZATIONS TABLE")
            print("-" * 30)

            org_count_query = "SELECT COUNT(*) as total FROM organizations;"
            total_orgs = pd.read_sql_query(org_count_query, conn)['total'][0]
            print(f"Total organizations: {total_orgs}")

        print(f"\nDatabase inspection complete!")

    except Exception as e:
        print(f"Error inspecting database: {e}")

    finally:
        conn.close()


def show_sample_animals(db_path="data/shelter_data.db", limit=10):
    """Show sample animal records"""
    if not os.path.exists(db_path):
        print(f"Database not found at {db_path}")
        return

    conn = sqlite3.connect(db_path)

    try:
        query = f"""
        SELECT 
            name, 
            species, 
            breed_primary, 
            age, 
            gender, 
            size, 
            status,
            city,
            state
        FROM animals 
        LIMIT {limit};
        """

        df = pd.read_sql_query(query, conn)

        if len(df) > 0:
            print(f"\nSAMPLE ANIMALS (showing {len(df)} records)")
            print("=" * 80)
            print(df.to_string(index=False))
        else:
            print("No animals found in database")

    except Exception as e:
        print(f"Error fetching sample animals: {e}")

    finally:
        conn.close()


def export_to_csv(db_path="data/shelter_data.db", output_dir="outputs"):
    """Export database tables to CSV files"""
    if not os.path.exists(db_path):
        print(f"Database not found at {db_path}")
        return

    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    conn = sqlite3.connect(db_path)

    try:
        # Export animals table
        animals_df = pd.read_sql_query("SELECT * FROM animals;", conn)
        animals_csv_path = f"{output_dir}/animals_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
        animals_df.to_csv(animals_csv_path, index=False)
        print(f"Exported {len(animals_df)} animals to {animals_csv_path}")

        # Export organizations table if it exists
        try:
            orgs_df = pd.read_sql_query("SELECT * FROM organizations;", conn)
            if len(orgs_df) > 0:
                orgs_csv_path = f"{output_dir}/organizations_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
                orgs_df.to_csv(orgs_csv_path, index=False)
                print(f"Exported {len(orgs_df)} organizations to {orgs_csv_path}")
        except:
            print("No organizations table found")

    except Exception as e:
        print(f"Error exporting data: {e}")

    finally:
        conn.close()


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description='Inspect shelter database')
    parser.add_argument('--action', choices=['inspect', 'sample', 'export'],
                        default='inspect', help='Action to perform')
    parser.add_argument('--db', default='data/shelter_data.db',
                        help='Path to database file')
    parser.add_argument('--limit', type=int, default=10,
                        help='Number of sample records to show')

    args = parser.parse_args()

    if args.action == 'inspect':
        inspect_database(args.db)
    elif args.action == 'sample':
        show_sample_animals(args.db, args.limit)
    elif args.action == 'export':
        export_to_csv(args.db)