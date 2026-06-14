import streamlit as st
from repositories import user_repo
from database import get_client
from typing import Optional


class TomatoService:
    @staticmethod
    def get_balance(user_id: str) -> int:
        user = user_repo.get_user_by_id(user_id)
        return user.get("tomato_balance", 0) if user else 0

    @staticmethod
    def credit(
        user_id: str,
        amount: int,
        description: str,
        txn_type: str = "general",
        related_id: Optional[str] = None,
    ) -> bool:
        try:
            current_balance = TomatoService.get_balance(user_id)
            new_balance = current_balance + amount
            user_repo.update_tomato_balance(user_id, new_balance)

            client = get_client()
            txn_data = {
                "user_id": user_id,
                "amount": amount,
                "description": description,
                "type": txn_type,
                "balance_after": new_balance,
            }
            if related_id:
                txn_data["related_id"] = related_id
            client.table("tomato_transactions").insert(txn_data).execute()
            st.cache_data.clear()
            return True
        except Exception as e:
            print(f"[tomato_service] credit error: {e}")
            return False

    @staticmethod
    def debit(
        user_id: str,
        amount: int,
        description: str,
        txn_type: str = "delivery_spend",
        related_id: Optional[str] = None,
    ) -> tuple:
        current_balance = TomatoService.get_balance(user_id)
        if current_balance < amount:
            return False, f"Insufficient tomatoes. Balance: {current_balance}, required: {amount}."

        try:
            new_balance = current_balance - amount
            user_repo.update_tomato_balance(user_id, new_balance)

            client = get_client()
            txn_data = {
                "user_id": user_id,
                "amount": -amount,
                "description": description,
                "type": txn_type,
                "balance_after": new_balance,
            }
            if related_id:
                txn_data["related_id"] = related_id
            client.table("tomato_transactions").insert(txn_data).execute()
            st.cache_data.clear()
            return True, ""
        except Exception as e:
            print(f"[tomato_service] debit error: {e}")
            return False, "Transaction failed. Please try again."

    @staticmethod
    def get_transactions(user_id: str) -> list:
        try:
            client = get_client()
            result = (
                client.table("tomato_transactions")
                .select("*")
                .eq("user_id", user_id)
                .order("created_at", desc=True)
                .execute()
            )
            return result.data or []
        except Exception as e:
            print(f"[tomato_service] get_transactions error: {e}")
            return []
