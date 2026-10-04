import {useEffect,useState} from "react";
import api from "../../api/client";
import EditProfileModal from "../../components/profile/EditProfileModal";
import {
Phone,
Globe,
MapPin,
Languages,
Volume2,
Mail,
Calendar,
CheckCircle,
CreditCard
} from "lucide-react";
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
<Phone size={24}/>
<h4>Phone</h4>
{user.phone || "Not set"}
</div>


<div className="profile-box">
<Globe size={24}/>
<h4>Country</h4>
{user.country || "Not set"}
</div>


<div className="profile-box">
<MapPin size={24}/>
<h4>City</h4>
{user.city || "Not set"}
</div>


<div className="profile-box">
<Languages size={24}/>
<h4>Language</h4>
{user.preferred_language}
</div>


<div className="profile-box">
<Volume2 size={24}/>
<h4>Tone</h4>
{user.preferred_tone}
</div>


</div>


<div className="profile-bottom">


<div className="profile-panel">

<h3>
Account Overview
</h3>


<div className="overview-row">
<Mail size={20}/>
<div>
<p>Email Address</p>
<strong>{user.email}</strong>
</div>
</div>


<div className="overview-row">
<Calendar size={20}/>
<div>
<p>Member Since</p>
<strong>August 2026</strong>
</div>
</div>


<div className="overview-row">
<CheckCircle size={20}/>
<div>
<p>Account Status</p>
<strong className="active-status">
Active
</strong>
</div>
</div>


<div className="overview-row">
<CreditCard size={20}/>
<div>
<p>Plan</p>
<strong>
Professional Plan
</strong>
</div>
</div>


</div>


<div className="profile-panel">

<h3>
Recent Activity
</h3>

<div className="activity">
<span className="activity-icon success">✓</span>
Logged in successfully
</div>

<div className="activity">
<span className="activity-icon edit">✎</span>
Updated profile information
</div>

<div className="activity">
<span className="activity-icon file">▣</span>
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
