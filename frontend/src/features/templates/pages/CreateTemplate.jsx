import Button from "../../../shared/ui/Button";
import {useState} from "react";
import {useNavigate} from "react-router-dom";
import api from "../../../shared/api/client";


export default function CreateTemplate(){

const navigate = useNavigate();


const [form,setForm]=useState({
name:"",
purpose:"",
description:"",
tone:"",
language:"",
subject:"",
body:""
});



function change(e){

setForm({
...form,
[e.target.name]:e.target.value
});

}



async function submit(e){

e.preventDefault();

try{

await api.post("/templates/",form);

navigate("/templates");

}
catch(err){

console.log("CREATE TEMPLATE ERROR:");
console.log(err.response?.data || err);

alert(
JSON.stringify(err.response?.data || err)
);

}

}



return (

<div className="page">


<Button
variant="secondary"
onClick={()=>navigate("/templates")}
>
← Back
</Button>


<h1>
Create Template
</h1>


<p className="subtitle">
Create reusable email template
</p>



<div className="form-card">


<form onSubmit={submit} className="form-stack">


<label className="form-field">Template Name<input id="template-name" name="name" onChange={change} /></label>


<label className="form-field">Purpose<input id="template-purpose" name="purpose" onChange={change} /></label>


<label className="form-field">Description<textarea id="template-description" name="description" rows="5" onChange={change} /></label>


<label className="form-field">Tone<input id="template-tone" name="tone" placeholder="Professional, friendly…" onChange={change} /></label>


<label className="form-field">Language<input id="template-language" name="language" onChange={change} /></label>


<label className="form-field">Email Subject<input id="template-subject" name="subject" onChange={change} /></label>


<label className="form-field">Email Body<textarea id="template-body" name="body" rows="8" onChange={change} /></label>


<Button type="submit">
Create Template
</Button>


</form>


</div>


</div>

)

}
