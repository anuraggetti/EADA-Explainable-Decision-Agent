"""
E.A.D.A Decision History Routes

Handles the history page and provides recent
decision data to the dashboard.
"""

from flask import Blueprint, jsonify, render_template, request

from services import services


history_bp = Blueprint(
    "history",
    __name__
)


@history_bp.route(
    "/history",
    methods=["GET"]
)
def history_page():
    """
    Render the decision history page or return
    recent decision history as JSON.
    """

    try:

        # Dashboard requests JSON data
        if request.args.get("format") == "json":

            records = services.database.get_recent_decisions(
                limit=10
            )

            return jsonify({
                "status": "success",
                "history": records,
                "count": len(records)
            }), 200

        # Normal Decision History page
        return render_template(
            "history.html"
        )

    except Exception as error:

        print(
            "\n========== HISTORY ERROR =========="
        )

        print(error)

        print(
            "===================================\n"
        )

        if request.args.get("format") == "json":

            return jsonify({
                "status": "error",
                "message": "Unable to load decision history.",
                "details": str(error)
            }), 500

        return render_template(
            "history.html"
        )