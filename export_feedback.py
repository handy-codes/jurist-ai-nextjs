import csv
from config.database import SessionLocal
from models.database_models import Feedback, Query, User


def export_feedback_to_csv(filename="all_feedback.csv"):
    session = SessionLocal()
    feedbacks = session.query(Feedback).all()
    with open(filename, mode="w", newline='', encoding="utf-8") as file:
        writer = csv.writer(file)
        writer.writerow([
            "Feedback ID", "User ID", "User Email", "Query ID", "Question", "Response", "Rating", "Is Helpful", "Feedback Text", "Created At"
        ])
        for fb in feedbacks:
            user_email = fb.user.email if fb.user else "N/A"
            question = fb.query.question if fb.query else "N/A"
            response = fb.query.response if fb.query else "N/A"
            writer.writerow([
                fb.id, fb.user_id, user_email, fb.query_id, question, response, fb.rating, fb.is_helpful, fb.feedback_text, fb.created_at
            ])
    session.close()
    print(f"Exported {len(feedbacks)} feedback entries to {filename}")


def print_all_feedback():
    session = SessionLocal()
    feedbacks = session.query(Feedback).all()
    for fb in feedbacks:
        print("-"*60)
        print(f"Feedback ID: {fb.id}")
        print(f"User ID: {fb.user_id}")
        print(f"User Email: {fb.user.email if fb.user else 'N/A'}")
        print(f"Query ID: {fb.query_id}")
        print(f"Question: {fb.query.question if fb.query else 'N/A'}")
        print(f"Response: {fb.query.response if fb.query else 'N/A'}")
        print(f"Rating: {fb.rating}")
        print(f"Is Helpful: {fb.is_helpful}")
        print(f"Feedback Text: {fb.feedback_text}")
        print(f"Created At: {fb.created_at}")
    session.close()


if __name__ == "__main__":
    print("Choose an option:")
    print("1. Print all feedback to console")
    print("2. Export all feedback to CSV")
    choice = input("Enter 1 or 2: ").strip()
    if choice == "1":
        print_all_feedback()
    elif choice == "2":
        export_feedback_to_csv()
    else:
        print("Invalid choice.")
