from __future__ import annotations

import json
import os
from typing import Any

import requests
import streamlit as st
from dotenv import load_dotenv

load_dotenv()

DEFAULT_BASE_URL = os.getenv("AGENT_API_URL", "http://127.0.0.1:8000")
DEFAULT_TIMEOUT = 30

st.set_page_config(
    page_title="Analytics Data Agent tester", page_icon="📊", layout="wide"
)

st.title("Analytics Data Agent – Streamlit sandbox")
st.caption(
    "Interface légère pour piloter les endpoints FastAPI exposés dans app/api.py."
)


def _format_json(text: str | None) -> Any:
    if not text:
        return None
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        return None


def call_api(
    method: str,
    *,
    base_url: str,
    path: str,
    timeout: int,
    headers: dict[str, str] | None = None,
    params: dict[str, Any] | None = None,
    json_body: dict[str, Any] | None = None,
) -> requests.Response:
    url = f"{base_url.rstrip('/')}{path}"
    response = requests.request(
        method=method,
        url=url,
        params=params,
        json=json_body,
        headers=headers,
        timeout=timeout,
    )
    return response


def render_response(response: requests.Response) -> None:
    st.markdown(
        f"**Status:** {response.status_code} "
        f"{'✅' if response.ok else '⚠️'} – {response.reason}"
    )
    st.write(f"URL appelée : `{response.request.method} {response.request.url}`")
    st.write(f"Durée : {response.elapsed.total_seconds():.2f}s")

    with st.expander("Headers de réponse"):
        st.json(dict(response.headers))

    parsed_json = _format_json(response.text)
    if parsed_json is not None:
        st.subheader("Payload JSON")
        st.json(parsed_json)
    elif response.text:
        st.subheader("Payload brut")
        st.code(response.text)
    else:
        st.info("La réponse ne contient pas de corps.")


with st.sidebar:
    base_url = st.text_input("API base URL", value=DEFAULT_BASE_URL)
    timeout = st.slider(
        "Timeout requêtes (s)",
        min_value=5,
        max_value=120,
        value=DEFAULT_TIMEOUT,
        step=5,
    )

    identity_token = st.text_input(
        "Identity token (Cloud Run / IAP)", placeholder="eyJhbGciOi...", type="password"
    ).strip()
    formatted_bearer = None
    if identity_token:
        trimmed = identity_token.replace("Bearer ", "").strip()
        formatted_bearer = f"Bearer {trimmed}"

    headers = {}
    if formatted_bearer:
        headers["Authorization"] = formatted_bearer

    if not headers:
        headers = None

    st.divider()

tab_health, tab_agent, tab_chat = st.tabs(
    ["Health", "Agent lifecycle", "Chat playground"]
)


with tab_health:
    st.subheader("Ping /health")
    st.write("Permet de vérifier que l'API répond bien avant d'aller plus loin.")
    if st.button("Appeler GET /health", type="primary", use_container_width=True):
        try:
            response = call_api(
                "GET",
                base_url=base_url,
                path="/health",
                timeout=timeout,
                headers=headers,
            )
            render_response(response)
        except requests.RequestException as exc:
            st.error(f"Échec de la requête: {exc}")


with tab_agent:
    st.subheader("Pilotage de l'agent Gemini Data Analytics")

    col_get, col_list = st.columns(2)
    with col_get:
        st.markdown("**GET /agent** – lecture de l'agent configuré.")
        if st.button(
            "Récupérer l'agent", key="btn_get_agent", use_container_width=True
        ):
            try:
                response = call_api(
                    "GET",
                    base_url=base_url,
                    path="/agent",
                    timeout=timeout,
                    headers=headers,
                )
                render_response(response)
            except requests.RequestException as exc:
                st.error(f"Erreur: {exc}")

    with col_list:
        st.markdown("**GET /agents** – liste des agents disponibles.")
        if st.button(
            "Lister les agents", key="btn_list_agents", use_container_width=True
        ):
            try:
                response = call_api(
                    "GET",
                    base_url=base_url,
                    path="/agents",
                    timeout=timeout,
                    headers=headers,
                )
                render_response(response)
            except requests.RequestException as exc:
                st.error(f"Erreur: {exc}")

    st.divider()
    st.markdown("### Synchronisation de l'agent (/agent)")
    sync_cols = st.columns(2)
    with sync_cols[0]:
        st.markdown("Créer l'agent s'il n'existe pas.")
        create_agent_id = st.text_input(
            "Data agent ID (optionnel)",
            key="create_agent_id_input",
            placeholder="senior_residence_analytics_agent",
            help="Laisse vide pour utiliser la valeur de l'environnement backend.",
        )
        if st.button("POST /agent", key="btn_create_agent", use_container_width=True):
            payload = None
            if create_agent_id.strip():
                payload = {"data_agent_id": create_agent_id.strip()}
            try:
                response = call_api(
                    "POST",
                    base_url=base_url,
                    path="/agent",
                    timeout=timeout,
                    headers=headers,
                    json_body=payload,
                )
                render_response(response)
            except requests.RequestException as exc:
                st.error(f"Erreur: {exc}")

    with sync_cols[1]:
        st.markdown("Mettre à jour la définition déjà déployée.")
        if st.button("PUT /agent", key="btn_update_agent", use_container_width=True):
            try:
                response = call_api(
                    "PUT",
                    base_url=base_url,
                    path="/agent",
                    timeout=timeout,
                    headers=headers,
                )
                render_response(response)
            except requests.RequestException as exc:
                st.error(f"Erreur: {exc}")

    st.divider()
    st.markdown("### Suppression ciblée (/agent/{agent_id})")
    with st.form("delete_agent_form"):
        agent_id = st.text_input("ID de l'agent à supprimer")
        force = st.checkbox("Force delete (ignore PRECONDITION_FAILED)")
        delete_submitted = st.form_submit_button(
            "DELETE /agent/{agent_id}", use_container_width=True
        )

    if delete_submitted:
        if not agent_id:
            st.warning("Merci de fournir un identifiant d'agent.")
        else:
            try:
                response = call_api(
                    "DELETE",
                    base_url=base_url,
                    path=f"/agent/{agent_id}",
                    timeout=timeout,
                    headers=headers,
                    params={"force": str(force).lower()},
                )
                if response.status_code == 204:
                    st.success("Suppression demandée avec succès (204 No Content).")
                render_response(response)
            except requests.RequestException as exc:
                st.error(f"Erreur: {exc}")


with tab_chat:
    st.subheader("Playground de discussion (/chat)")
    st.write(
        "Définis une question, optionnellement un `conversation_id`, "
        "et coche `preview` pour activer la génération SQL."
    )

    with st.form("chat_form"):
        question = st.text_area(
            "Question",
            height=150,
            placeholder="Ex: Donne-moi la facturation moyenne par résident.",
        )
        conversation_id = st.text_input(
            "Conversation ID (optionnel)",
            placeholder="api-123...",
        )
        preview = st.checkbox("Mode preview (retour SQL)", value=False)
        submitted = st.form_submit_button(
            "Envoyer la requête POST /chat", use_container_width=True
        )

    if submitted:
        if not question.strip():
            st.warning("La question est obligatoire.")
        else:
            payload: dict[str, Any] = {
                "question": question.strip(),
                "preview": preview,
            }
            if conversation_id.strip():
                payload["conversation_id"] = conversation_id.strip()

            try:
                response = call_api(
                    "POST",
                    base_url=base_url,
                    path="/chat",
                    timeout=timeout,
                    headers=headers,
                    json_body=payload,
                )
            except requests.RequestException as exc:
                st.error(f"Erreur: {exc}")
            else:
                if not response.ok:
                    render_response(response)
                else:
                    data = response.json()
                    st.success(f"Conversation ID: {data.get('conversation_id', 'N/A')}")
                    st.markdown("**Réponse:**")
                    st.write(data.get("answer") or "(Réponse vide)")
                    if data.get("generated_sql"):
                        st.markdown("**SQL généré:**")
                        st.code(data["generated_sql"], language="sql")
