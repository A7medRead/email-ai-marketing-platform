import { BrowserRouter, Routes, Route } from "react-router-dom";

import Login from "../features/auth/pages/Login";
import Register from "../features/auth/pages/Register";
import ResetPassword from "../features/auth/pages/ResetPassword";
import Profile from "../features/profile/pages/Profile";
import ForgotPassword from "../features/auth/pages/ForgotPassword";
import Dashboard from "../features/dashboard/pages/Dashboard";
import Campaigns from "../features/campaigns/pages/Campaigns";
import CreateCampaign from "../features/campaigns/pages/CreateCampaign";
import Analytics from "../features/analytics/pages/Analytics";
import CampaignPerformance from "../features/campaigns/pages/CampaignPerformance";
import CampaignDetails from "../features/campaigns/pages/CampaignDetails";
import EditCampaign from "../features/campaigns/pages/EditCampaign";

import Templates from "../features/templates/pages/Templates";
import CreateTemplate from "../features/templates/pages/CreateTemplate";
import EditTemplate from "../features/templates/pages/EditTemplate";
import Emails from "../features/email-generation/pages/Emails";
import CreateEmail from "../features/email-generation/pages/CreateEmail";
import EmailDetails from "../features/email-generation/pages/EmailDetails";
import Layout from "../layouts/Layout";
import ProtectedRoute from "../layouts/ProtectedRoute";
import SenderAccounts from "../features/sender-accounts/pages/SenderAccounts";
import CreateSenderAccount from "../features/sender-accounts/pages/CreateSenderAccount";
import EditSenderAccount from "../features/sender-accounts/pages/EditSenderAccount";
import Contacts from "../features/contacts/pages/Contacts";
import CreateContact from "../features/contacts/pages/CreateContact";
import ContactDetails from "../features/contacts/pages/ContactDetails";
import EditContact from "../features/contacts/pages/EditContact";
import ContactLists from "../features/contact-lists/pages/ContactLists";
import CreateContactList from "../features/contact-lists/pages/CreateContactList";
import ManageContactList from "../features/contact-lists/pages/ManageContactList";



function App(){

return (

<BrowserRouter>

<Routes>


<Route
path="/"
element={<Login />}
/>


<Route
path="/register"
element={<Register />}
/>


<Route
path="/forgot-password"
element={<ForgotPassword />}
/>

<Route path="/reset-password" element={<ResetPassword />} />


<Route
element={
    <ProtectedRoute>
        <Layout />
    </ProtectedRoute>
}
>

<Route
path="/profile"
element={<Profile />}
/>

<Route
path="/dashboard"
element={<Dashboard />}
/>


<Route
path="/campaigns"
element={<Campaigns />}
/>

<Route
path="/campaigns/create"
element={<CreateCampaign />}
/>

<Route
path="/campaigns/:id/analytics"
element={<Analytics />}
/>

<Route
path="/campaigns/:id/performance"
element={<CampaignPerformance />}
/>

<Route
path="/campaigns/:id/details"
element={<CampaignDetails />}
/>


<Route
path="/campaigns/:id/edit"
element={<EditCampaign />}
/>

<Route path="/templates" element={<Templates />} />
<Route path="/templates/create" element={<CreateTemplate />} />
<Route path="/templates/:id/edit" element={<EditTemplate />} />

<Route path="/emails" element={<Emails />} />
<Route path="/emails/create" element={<CreateEmail />} />
<Route path="/emails/:id" element={<EmailDetails />} />


<Route path="/senders" element={<SenderAccounts />} />
<Route path="/senders/create" element={<CreateSenderAccount />} />
<Route path="/senders/:id/edit" element={<EditSenderAccount />} />

<Route path="/contacts" element={<Contacts />} />
<Route path="/contacts/create" element={<CreateContact />} />
<Route path="/contacts/:id/edit" element={<EditContact />} />
<Route path="/contacts/:id" element={<ContactDetails />} />
<Route path="/contact-lists/:id/manage" element={<ManageContactList />} />


<Route path="/contact-lists" element={<ContactLists />} />
<Route path="/contact-lists/create" element={<CreateContactList />} />

</Route>


</Routes>

</BrowserRouter>

)

}

export default App;
