import Button from "../../components/Button";
import "./ContactLists.css";
import {useState} from "react";
import {useNavigate} from "react-router-dom";
import api from "../../api/client";

export default function CreateContactList(){

const navigate = useNavigate();

const [form,setForm] = useState({
    name:"",
    description:""
});


function change(e){

setForm(prev=>({
    ...prev,
    [e.target.name]:e.target.value
}));

}


async function submit(e){

e.preventDefault();

try{

await api.post("/contact-lists/",form);

navigate("/contact-lists");

}
catch(err){

console.log(err.response?.data || err);

}

}


return (

<div className="page">

<Button
variant="secondary"
onClick={()=>navigate("/contact-lists")}
>
← Back
</Button>

<h1>
Create Contact List
</h1>

<p className="subtitle">
Create customer group
</p>


<form
onSubmit={submit}
style={{
display:"grid",
gap:"18px",
maxWidth:"600px"
}}
>

<input
name="name"
placeholder="List Name"
onChange={change}
/>


<textarea
name="description"
placeholder="Description"
rows="5"
onChange={change}
/>


<Button>
Create List
</Button>


</form>


</div>

)

}
