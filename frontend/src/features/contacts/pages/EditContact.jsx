import Button from "../../../shared/ui/Button";
import {useEffect,useState} from "react";
import {useParams,useNavigate} from "react-router-dom";
import api from "../../../shared/api/client";

export default function EditContact(){

const {id}=useParams();
const navigate=useNavigate();

const [form,setForm]=useState({
first_name:"",
last_name:"",
email:"",
company:"",
phone:"",
position:""
});
const [error,setError]=useState("");


useEffect(()=>{

api.get(`/contacts/${id}`)
.then(res=>{
setForm(res.data);
}).catch(()=>setError("Could not load this contact. Please go back and try again."));

},[id]);


function change(e){

setForm({
...form,
[e.target.name]:e.target.value
});

}


async function save(){

await api.put(`/contacts/${id}`,form);

navigate(`/contacts/${id}`);

}


return (

<div className="page">

<Button
variant="secondary"
onClick={()=>navigate(`/contacts/${id}`)}
>
← Back
</Button>

<h1>Edit Contact</h1>


<form className="form-card form-stack" onSubmit={async e=>{e.preventDefault();try{await save();}catch{setError("Could not save changes. Please try again.");}}}>

{[
"first_name",
"last_name",
"email",
"company",
"phone",
"position"
].map(key=>(

<label className="form-field" key={key}>{key.replaceAll("_", " ").replace(/^\w/, c=>c.toUpperCase())}<input name={key} type={key === "email" ? "email" : "text"} value={form[key] || ""} onChange={change} /></label>

))}


{error && <p role="alert" className="form-error">{error}</p>}
<Button type="submit">
Save Changes
</Button>


</form>

</div>

)

}
