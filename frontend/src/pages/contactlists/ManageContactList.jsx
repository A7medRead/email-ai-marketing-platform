import Button from "../../components/Button";
import "./ContactLists.css";
import {useEffect,useState} from "react";
import {useParams,useNavigate} from "react-router-dom";
import api from "../../api/client";


export default function ManageContactList(){

const {id}=useParams();
const navigate=useNavigate();

const [list,setList]=useState(null);
const [allContacts,setAllContacts]=useState([]);
const [members,setMembers]=useState([]);
const [message,setMessage]=useState("");


async function load(){

const lists = await api.get("/contact-lists/");
const found = lists.data.find(
x=>String(x.id)===String(id)
);

setList(found);


const contacts = await api.get("/contacts/");
setAllContacts(contacts.data);


const current = await api.get(`/contact-lists/${id}/contacts`);
setMembers(current.data);

}



useEffect(()=>{

load();

},[id]);



async function addContact(contactId){

await api.post(
`/contact-lists/${id}/contacts/${contactId}`
);

setMessage("Contact added");

load();

}



async function removeContact(contactId){

await api.delete(
`/contact-lists/${id}/contacts/${contactId}`
);

setMessage("Contact removed");

load();

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

<div className="contactlists-card" key={contact.id}>

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
onClick={()=>removeContact(contact.id)}
>
Remove
</Button>

</div>

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

<div className="contactlists-card" key={contact.id}>


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
onClick={()=>addContact(contact.id)}
>
Add to List
</Button>


</div>

))
}

</div>


</div>

)

}
