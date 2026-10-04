import { useEffect, useState } from "react";
import api from "../../api/client";

export default function Profile(){

    const [user,setUser]=useState(null);
    const [edit,setEdit]=useState(false);
    const [form,setForm]=useState({});
    const [uploading,setUploading]=useState(false);


    async function loadUser(){

        const res = await api.get("/users/me");

        setUser(res.data);
        setForm(res.data);

    }


    useEffect(()=>{

        loadUser();

    },[]);



    async function save(){

        await api.put("/users/me",form);

        await loadUser();

        setEdit(false);

    }


    async function uploadAvatar(e){

        const file = e.target.files[0];

        if(!file) return;


        const data = new FormData();

        data.append("file",file);


        setUploading(true);

        await api.put(
            "/users/me/avatar",
            data,
            {
                headers:{
                    "Content-Type":"multipart/form-data"
                }
            }
        );


        await loadUser();

        setUploading(false);

    }



    if(!user){

        return <div>Loading...</div>;

    }


    return (

        <div className="profile-page">

            <div className="profile-card">


                <h1>
                    Profile
                </h1>


                <input
                    type="file"
                    accept="image/*"
                    onChange={uploadAvatar}
                />


                {uploading && <p>Uploading...</p>}


                <img
                    src={
                        user.avatar
                        ? "http://127.0.0.1:8000" + user.avatar
                        : "https://via.placeholder.com/100"
                    }
                    width="100"
                    height="100"
                />


                {!edit ? (

                    <>

                    <h2>
                        {user.name}
                    </h2>

                    <p>{user.email}</p>

                    <p>
                        Phone: {user.phone || "Not set"}
                    </p>

                    <p>
                        Country: {user.country || "Not set"}
                    </p>

                    <p>
                        City: {user.city || "Not set"}
                    </p>

                    <p>
                        Language: {user.preferred_language}
                    </p>

                    <p>
                        Tone: {user.preferred_tone}
                    </p>

                    <button onClick={()=>setEdit(true)}>
                        Edit Profile
                    </button>

                    </>

                ) : (

                    <>

                    <input
                    value={form.name || ""}
                    onChange={e=>setForm({...form,name:e.target.value})}
                    placeholder="Name"
                    />


                    <input
                    value={form.phone || ""}
                    onChange={e=>setForm({...form,phone:e.target.value})}
                    placeholder="Phone"
                    />


                    <input
                    value={form.country || ""}
                    onChange={e=>setForm({...form,country:e.target.value})}
                    placeholder="Country"
                    />


                    <input
                    value={form.city || ""}
                    onChange={e=>setForm({...form,city:e.target.value})}
                    placeholder="City"
                    />


                    <button onClick={save}>
                        Save
                    </button>


                    <button onClick={()=>setEdit(false)}>
                        Cancel
                    </button>


                    </>

                )}


            </div>

        </div>

    );

}
