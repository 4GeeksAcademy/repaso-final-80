import React, { useActionState, useContext, useEffect } from "react";
import { useNavigate } from "react-router-dom";
import { Context } from "../store/appContext";

export const Perfil = () => {
const {store, actions} = useContext(Context)
    const navigate = useNavigate()

    useEffect(()=>{
        if (!localStorage.getItem('token')) navigate('/')
            actions.getUserInfo()
    },[])

    const handleLogout = () => {
        localStorage.removeItem('token')
        navigate('/')
    }

    return (
        <div>
            <h2>
                Perfil!
            </h2>
            <p>correo: {store.user?.email}</p>
            <button onClick={handleLogout}>
                logout
            </button>
        </div>
    )
}