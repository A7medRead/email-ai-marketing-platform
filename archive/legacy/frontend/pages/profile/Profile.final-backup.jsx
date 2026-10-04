import {useEffect,useState} from "react";
import api from "../../api/client";
import EditProfileModal from "../../components/profile/EditProfileModal";
import "./Profile.css";


export default function Profile(){

const [user,setUser]=useState(null);
const [edit,setEdit]=useState(false);
const [form,setForm]=useState({});


async function loadUser(){
 const res=await api.get("/users/me");
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

const file=e.target.files[0];

if(!file)return;

const data=new FormData();
data.append("file",file);

await api.put(
"/users/me/avatar",
data,
{
headers:{
"Content-Type":"multipart/form-data"
}
}
);

loadUser();

}



if(!user)
return <div>Loading...</div>;



return (

<div className="profile-page">


<div className="profile-title">

<h1>
👤 Profile
</h1>

<div className="profile-breadcrumb">
Home &nbsp; › &nbsp; Profile
</div>

</div>


<div className="profile-hero">


<div className="profile-main">

<div>

<img
className="profile-avatar"
src={
user.avatar
?"http://127.0.0.1:8000"+user.avatar
:"https://via.placeholder.com/150"
}
/>

<label className="avatar-edit">
<input
type="file"
accept="image/*"
onChange={uploadAvatar}
/>
✎
</label>

</div>


<div>

<h1 className="profile-name">
{user.name}
</h1>

<span className="profile-badge">
{user.preferred_tone || "Professional"}
</span>

<p className="profile-email">
{user.email}
</p>


<button
className="profile-btn"
onClick={()=>setEdit(true)}
>
✎ Edit Profile
</button>

</div>


</div>


</div>



<div className="profile-stats">


<div className="profile-box">
<h4>Phone</h4>
{user.phone || "Not set"}
</div>


<div className="profile-box">
<h4>Country</h4>
{user.country || "Not set"}
</div>


<div className="profile-box">
<h4>City</h4>
{user.city || "Not set"}
</div>


<div className="profile-box">
<h4>Language</h4>
{user.preferred_language}
</div>


<div className="profile-box">
<h4>Tone</h4>
{user.preferred_tone}
</div>


</div>



<div className="profile-bottom">


<div className="profile-panel">

<h3>
Account Overview
</h3>

<p>Email Address</p>
<strong>{user.email}</strong>

<p>Account Status</p>
<strong>Active</strong>

</div>



<div className="profile-panel">

<h3>
Recent Activity
</h3>

<div className="activity">
Logged in successfully
</div>

<div className="activity">
Updated profile information
</div>

<div className="activity">
Changed email template
</div>


</div>


</div>




{edit && (

<EditProfileModal
    form={form}
    setForm={setForm}
    save={save}
    close={()=>setEdit(false)}
    uploadAvatar={uploadAvatar}
/>

)}




</div>

)

}
