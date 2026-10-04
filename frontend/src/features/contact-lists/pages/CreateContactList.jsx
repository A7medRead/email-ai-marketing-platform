import Button from "../../../shared/ui/Button";
import "./ContactLists.css";
import {useState} from "react";
import {useNavigate} from "react-router-dom";
import api from "../../../shared/api/client";

export default function CreateContactList(){

const navigate = useNavigate();

const [form,setForm] = useState({
    name:"",
    description:""
});
const [error,setError]=useState("");


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
setError("Could not create the contact list. Please check the details and try again.");

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


<div className="form-card"><form onSubmit={submit} className="form-stack">

<label className="form-field">List Name<input required name="name" value={form.name} onChange={change} />
</label>

<label className="form-field">Description<textarea name="description" value={form.description} rows="5" onChange={change} /></label>
{error && <p role="alert" className="form-error">{error}</p>}


<Button type="submit">
Create List
</Button>


</form></div>


</div>

)

}
