import Button from "../../../shared/ui/Button";
import Card from "../../../shared/ui/Card";
import "./ContactLists.css";
import {useCallback,useEffect,useState} from "react";
import {useParams,useNavigate} from "react-router-dom";
import api from "../../../shared/api/client";


export default function ManageContactList(){

const {id}=useParams();
const navigate=useNavigate();

const [list,setList]=useState(null);
const [allContacts,setAllContacts]=useState([]);
const [members,setMembers]=useState([]);
const [message,setMessage]=useState("");
const [loading,setLoading]=useState(false);


const load = useCallback(async () => {

const lists = await api.get("/contact-lists/");
const found = lists.data.find(
x=>String(x.id)===String(id)
);

setList(found);


const contacts = await api.get("/contacts/");
setAllContacts(contacts.data);


const current = await api.get(`/contact-lists/${id}/contacts`);
setMembers(current.data);

}, [id]);



useEffect(()=>{
// eslint-disable-next-line react-hooks/set-state-in-effect -- load starts async API requests.
load();
},[load]);



async function addContact(contactId){

try{

setLoading(true);

await api.post(
`/contact-lists/${id}/contacts/${contactId}`
);

setMessage("Contact added");

await load();

}
finally{

setLoading(false);

}

}



async function removeContact(contactId){

try{

setLoading(true);

await api.delete(
`/contact-lists/${id}/contacts/${contactId}`
);

setMessage("Contact removed");

await load();

}
finally{

setLoading(false);

}

}



if(!list)
return <h2>Loading...</h2>;



const memberIds = members.map(x=>x.id);



return (

<div className="page">


<Button
variant="secondary"
onClick={()=>navigate("/contact-lists")}
>
← Back
</Button>


<h1>{list.name}</h1>

<p className="subtitle">
Manage contacts
</p>


{message && <p>{message}</p>}



<h2>Members ({members.length})</h2>


<div className="contactlists-cards">

{
members.map(contact=>(

<Card className="contactlists-card" key={contact.id}>

<div className="contactlists-avatar">
{contact.first_name?.[0]}
</div>

<h2>
{contact.first_name} {contact.last_name}
</h2>

<p>
📧 {contact.email}
</p>

<Button
variant="danger"
disabled={loading}
onClick={()=>removeContact(contact.id)}
>
{loading ? "Removing..." : "Remove"}
</Button>

</Card>

))
}

</div>



<h2 style={{marginTop:"40px"}}>
Available Contacts
</h2>


<div className="contactlists-cards">

{
allContacts
.filter(c=>!memberIds.includes(c.id))
.map(contact=>(

<Card className="contactlists-card" key={contact.id}>


<div className="contactlists-avatar">
{contact.first_name?.[0]}
</div>


<h2>
{contact.first_name} {contact.last_name}
</h2>


<p>
📧 {contact.email}
</p>


<Button
disabled={loading}
onClick={()=>addContact(contact.id)}
>
{loading ? "Adding..." : "Add to List"}
</Button>


</Card>

))
}

</div>


</div>

)

}
