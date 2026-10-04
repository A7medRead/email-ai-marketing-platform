import Button from "../../../shared/ui/Button";
import {useEffect,useState} from "react";
import {useParams,useNavigate} from "react-router-dom";
import api from "../../../shared/api/client";


export default function EditTemplate(){

const {id}=useParams();
const navigate=useNavigate();


const [form,setForm]=useState({
name:"",
purpose:"",
description:"",
tone:"",
language:"",
subject:"",
body:""
});
const [error,setError]=useState("");


useEffect(()=>{

api.get("/templates/")
.then(res=>{

const template=res.data.find(
t=>String(t.id)===String(id)
);

if(template){
setForm({
name:template.name,
purpose:template.purpose,
description:template.description,
tone:template.tone,
language:template.language,
subject:template.subject || "",
body:template.body || ""
}).catch(()=>setError("Could not load this template."));
}

});

},[id]);



function change(e){

setForm({
...form,
[e.target.name]:e.target.value
});

}



async function submit(e){

e.preventDefault();

try{

await api.put(
`/templates/${id}`,
form
);

navigate("/templates");

}
catch(err){

console.log(JSON.stringify(err.response?.data || err, null, 2));
setError("Could not save this template. Please try again.");

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
Edit Template
</h1>



<div className="form-card"><form onSubmit={submit} className="form-stack">


<label className="form-field">Template Name<input required name="name" value={form.name} onChange={change} /></label>


<label className="form-field">Purpose<input name="purpose" value={form.purpose} onChange={change} /></label>


<label className="form-field">Description<textarea name="description" value={form.description} rows="5" onChange={change} /></label>


<label className="form-field">Tone<input name="tone" value={form.tone} onChange={change} /></label>


<label className="form-field">Language<input name="language" value={form.language} onChange={change} /></label>


<label className="form-field">Email Subject<input name="subject" value={form.subject} onChange={change} /></label>


<label className="form-field">Email Body<textarea name="body" value={form.body} rows="8" onChange={change} /></label>

{error && <p role="alert" className="form-error">{error}</p>}


<Button type="submit">
Save Changes
</Button>


</form></div>


</div>

)

}
