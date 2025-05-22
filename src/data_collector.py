# src/data_collector.py
import os
import time
from datetime import datetime
from dotenv import load_dotenv
from petfinder_api import PetfinderAPI
from database import DatabaseManager
import argparse


class ShelterDataCollector:
    def __init__(self):
        load_dotenv()

        self.api = PetfinderAPI(
            api_key=os.getenv('PETFINDER_API_KEY'),
            secret=os.getenv('PETFINDER_SECRET')
        )
        self.db = DatabaseManager()

        # Ensure database tables exist
        self.db.create_tables()

    def collect_animals(self, filters: dict, max_animals: int = None):
        """
        Collect animals based on filters

        Args:
            filters: Dictionary of API filters (type, location, etc.)
            max_animals: Maximum number of animals to collect (None for all)
        """
        print(f" Starting data collection with filters: {filters}")

        if not self.api.authenticate():
            print("Failed to authenticate with Petfinder API")
            return

        collected_count = 0
        animals = []
        page = 1

        while True:
            # Add pagination to filters
            current_filters = {**filters, 'page': page, 'limit': 100}

            print(f"Fetching page {page}...")
            batch = self.api.get_animals(**current_filters)

            if not batch:
                print("No more animals found")
                break

            # Save each animal to database
            for animal_data in batch:
                try:
                    saved_animal = self.db.save_animal(animal_data)
                    if saved_animal:
                        collected_count += 1

                        if collected_count % 100 == 0:
                            print(f"Saved {collected_count} animals so far...")

                        # Check if we've hit our limit
                        if max_animals and collected_count >= max_animals:
                            print(f"Reached target of {max_animals} animals")
                            return collected_count

                except Exception as e:
                    print(f"Error processing animal {animal_data.get('id')}: {e}")
                    continue

            animals.extend(batch)
            page += 1

            # Be nice to the API
            time.sleep(0.5)

        print(f"Collection complete! Saved {collected_count} animals")
        return collected_count

    def collect_sample_data(self, location: str = "90210", sample_size: int = 1000):
        """Collect a sample dataset for initial analysis"""
        print(f"Collecting sample of {sample_size} animals from {location}")

        # Collect dogs and cats from the specified location
        filters = {
            'location': location,
            'distance': 50,  # 50 mile radius
            'status': 'adoptable'
        }

        # Get dogs
        print("Collecting dogs...")
        dog_filters = {**filters, 'type': 'dog'}
        dogs_collected = self.collect_animals(dog_filters, sample_size // 2)

        # Get cats
        print("Collecting cats...")
        cat_filters = {**filters, 'type': 'cat'}
        cats_collected = self.collect_animals(cat_filters, sample_size // 2)

        total = dogs_collected + cats_collected
        print(f"Sample collection complete: {total} animals total")
        return total

    def collect_by_region(self, regions: list, animals_per_region: int = 500):
        """Collect data from multiple regions for geographic analysis"""
        total_collected = 0

        for region in regions:
            print(f"\nCollecting data from {region}")

            filters = {
                'location': region,
                'distance': 25,
                'status': 'adoptable'
            }

            collected = self.collect_animals(filters, animals_per_region)
            total_collected += collected

            # Small break between regions
            time.sleep(2)

        print(f"\nRegional collection complete: {total_collected} animals from {len(regions)} regions")
        return total_collected


def main():
    parser = argparse.ArgumentParser(description='Collect animal shelter data')
    parser.add_argument('--mode', choices=['sample', 'regional', 'custom'],
                        default='sample', help='Collection mode')
    parser.add_argument('--location', default='90210',
                        help='Location for sample collection')
    parser.add_argument('--size', type=int, default=1000,
                        help='Sample size for collection')

    args = parser.parse_args()

    collector = ShelterDataCollector()

    if args.mode == 'sample':
        collector.collect_sample_data(args.location, args.size)

    elif args.mode == 'regional':
        # Major US metropolitan areas for diverse sample
        regions = [
            "10001",  # New York, NY
            "90210",  # Los Angeles, CA
            "60601",  # Chicago, IL
            "77001",  # Houston, TX
            "85001",  # Phoenix, AZ
            "19101",  # Philadelphia, PA
            "78701",  # Austin, TX
            "32801",  # Orlando, FL
            "30301",  # Atlanta, GA
            "80201"  # Denver, CO
        ]
        collector.collect_by_region(regions, args.size // len(regions))

    elif args.mode == 'custom':
        # Custom collection - modify as needed
        filters = {
            'type': 'dog',
            'location': args.location,
            'distance': 50,
            'status': 'adoptable'
        }
        collector.collect_animals(filters, args.size)


if __name__ == "__main__":
    main()