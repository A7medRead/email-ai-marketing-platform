import { useEffect, useState } from "react";
import api from "../../api/client";

export default function ContactLists(){

    const [lists,setLists] = useState([]);

    useEffect(()=>{
        api.get("/contact-lists/")
        .then(res=>{
            setLists(res.data);
        })
        .catch(err=>{
            console.log(err);
        });
    },[]);


    return (
        <div>
            <h1>Contact Lists</h1>

            <table style={{width:"100%",marginTop:"30px"}}>
                <thead>
                    <tr>
                        <th>Name</th>
                        <th>Description</th>
                        <th>Contacts</th>
                    </tr>
                </thead>

                <tbody>
                    {lists.map(list=>(
                        <tr key={list.id}>
                            <td>{list.name}</td>
                            <td>{list.description}</td>
                            <td>{list.contacts_count ?? 0}</td>
                        </tr>
                    ))}
                </tbody>
            </table>
        </div>
    );
}
