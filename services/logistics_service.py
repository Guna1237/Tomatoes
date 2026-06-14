import streamlit as st
from repositories import logistics_repo
from repositories.notification_repo import add_notification
from services.tomato_service import TomatoService
from typing import Optional


VALID_TRANSITIONS = {
    "Accepted": "Picked Up",
    "Picked Up": "Delivered",
}


class LogisticsService:
    @staticmethod
    def get_open_requests(exclude_user_id: str) -> list:
        all_requests = logistics_repo.get_all_requests()
        return [
            r for r in all_requests
            if r.get("status") == "Created" and r.get("requester_id") != exclude_user_id
        ]

    @staticmethod
    def get_user_requests(user_id: str) -> list:
        all_requests = logistics_repo.get_all_requests()
        return [
            r for r in all_requests
            if r.get("requester_id") == user_id or r.get("helper_id") == user_id
        ]

    @staticmethod
    def create_request(
        title: str,
        description: str,
        pickup: str,
        delivery: str,
        tomatoes: int,
        user: dict,
    ) -> tuple:
        title = title.strip() if title else ""
        pickup = pickup.strip() if pickup else ""
        delivery = delivery.strip() if delivery else ""

        if not title:
            return None, "Request title cannot be empty."
        if not pickup:
            return None, "Pickup location cannot be empty."
        if not delivery:
            return None, "Delivery location cannot be empty."
        if tomatoes < 0:
            return None, "Tomato reward cannot be negative."

        if tomatoes > 0:
            success, error = TomatoService.debit(
                user_id=user["id"],
                amount=tomatoes,
                description=f"Delivery request: {title}",
                txn_type="delivery_spend",
            )
            if not success:
                return None, error

        data = {
            "title": title,
            "description": description,
            "pickup_location": pickup,
            "delivery_location": delivery,
            "tomato_reward": tomatoes,
            "requester_id": user["id"],
            "requester_name": user.get("name", ""),
            "status": "Created",
            "helper_id": None,
            "helper_name": None,
        }
        new_request = logistics_repo.create_request(data)
        if not new_request:
            if tomatoes > 0:
                TomatoService.credit(
                    user_id=user["id"],
                    amount=tomatoes,
                    description=f"Refund: failed delivery request '{title}'",
                    txn_type="bonus",
                )
            return None, "Failed to create request. Please try again."

        add_notification(
            user_id=user["id"],
            title="Delivery Request Created",
            content=f"Your delivery request '{title}' has been posted with a reward of {tomatoes} tomatoes.",
            notif_type="parcel",
            related_id=new_request.get("id"),
        )
        st.cache_data.clear()
        return new_request, ""

    @staticmethod
    def accept_request(req_id: str, user: dict) -> tuple:
        request = logistics_repo.get_request_by_id(req_id)
        if not request:
            return False, "Request not found."
        if request.get("status") != "Created":
            return False, "This request is no longer available."
        if request.get("requester_id") == user.get("id"):
            return False, "You cannot accept your own request."

        updated = logistics_repo.update_request(req_id, {
            "status": "Accepted",
            "helper_id": user["id"],
            "helper_name": user.get("name", ""),
        })
        if not updated:
            return False, "Failed to accept request. Please try again."

        add_notification(
            user_id=request["requester_id"],
            title="Delivery Request Accepted",
            content=f"Your request '{request.get('title', '')}' has been accepted by {user.get('name', 'someone')}.",
            notif_type="parcel",
            related_id=req_id,
        )
        st.cache_data.clear()
        return True, ""

    @staticmethod
    def update_status(req_id: str, new_status: str, user: dict) -> tuple:
        request = logistics_repo.get_request_by_id(req_id)
        if not request:
            return False, "Request not found."

        current_status = request.get("status")
        user_id = user.get("id")
        requester_id = request.get("requester_id")
        helper_id = request.get("helper_id")

        if new_status == "Cancelled":
            if current_status != "Created":
                return False, "Only requests with 'Created' status can be cancelled."
            if user_id != requester_id:
                return False, "Only the requester can cancel this request."
            logistics_repo.update_request(req_id, {"status": "Cancelled"})
            tomato_reward = request.get("tomato_reward", 0)
            if tomato_reward > 0:
                TomatoService.credit(
                    user_id=requester_id,
                    amount=tomato_reward,
                    description=f"Refund for cancelled delivery request: {request.get('title', '')}",
                    txn_type="bonus",
                    related_id=req_id,
                )
            add_notification(
                user_id=requester_id,
                title="Request Cancelled",
                content=f"Your delivery request '{request.get('title', '')}' has been cancelled.",
                notif_type="parcel",
                related_id=req_id,
            )
            st.cache_data.clear()
            return True, ""

        expected_next = VALID_TRANSITIONS.get(current_status)
        if expected_next != new_status:
            return False, f"Cannot transition from '{current_status}' to '{new_status}'."

        if user_id != helper_id:
            return False, "Only the assigned helper can update the status."

        logistics_repo.update_request(req_id, {"status": new_status})

        if new_status == "Delivered":
            tomato_reward = request.get("tomato_reward", 0)
            if tomato_reward > 0 and helper_id:
                TomatoService.credit(
                    user_id=helper_id,
                    amount=tomato_reward,
                    description=f"Delivery reward: {request.get('title', '')}",
                    txn_type="delivery_reward",
                    related_id=req_id,
                )
            add_notification(
                user_id=requester_id,
                title="Delivery Completed",
                content=f"Your delivery request '{request.get('title', '')}' has been delivered!",
                notif_type="parcel",
                related_id=req_id,
            )
            if helper_id:
                add_notification(
                    user_id=helper_id,
                    title="Delivery Rewarded",
                    content=f"You earned {request.get('tomato_reward', 0)} tomatoes for delivering '{request.get('title', '')}'.",
                    notif_type="parcel",
                    related_id=req_id,
                )
        elif new_status == "Picked Up":
            add_notification(
                user_id=requester_id,
                title="Package Picked Up",
                content=f"Your delivery request '{request.get('title', '')}' item has been picked up.",
                notif_type="parcel",
                related_id=req_id,
            )

        st.cache_data.clear()
        return True, ""
