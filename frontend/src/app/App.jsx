import { lazy, Suspense } from "react";
import { BrowserRouter, Routes, Route } from "react-router-dom";
import { Link } from "react-router-dom";

const Login = lazy(() => import("../features/auth/pages/Login"));
const Register = lazy(() => import("../features/auth/pages/Register"));
const ResetPassword = lazy(() => import("../features/auth/pages/ResetPassword"));
const Profile = lazy(() => import("../features/profile/pages/Profile"));
const SettingsPage = lazy(() => import("../features/settings/pages/Settings"));
const ForgotPassword = lazy(() => import("../features/auth/pages/ForgotPassword"));
const Dashboard = lazy(() => import("../features/dashboard/pages/Dashboard"));
const Campaigns = lazy(() => import("../features/campaigns/pages/Campaigns"));
const CreateCampaign = lazy(() => import("../features/campaigns/pages/CreateCampaign"));
const Analytics = lazy(() => import("../features/analytics/pages/Analytics"));
const CampaignPerformance = lazy(() => import("../features/campaigns/pages/CampaignPerformance"));
const CampaignDetails = lazy(() => import("../features/campaigns/pages/CampaignDetails"));
const EditCampaign = lazy(() => import("../features/campaigns/pages/EditCampaign"));

const Templates = lazy(() => import("../features/templates/pages/Templates"));
const CreateTemplate = lazy(() => import("../features/templates/pages/CreateTemplate"));
const EditTemplate = lazy(() => import("../features/templates/pages/EditTemplate"));
const Emails = lazy(() => import("../features/email-generation/pages/Emails"));
const CreateEmail = lazy(() => import("../features/email-generation/pages/CreateEmail"));
const EmailDetails = lazy(() => import("../features/email-generation/pages/EmailDetails"));
import Layout from "../layouts/Layout";
import ProtectedRoute from "../layouts/ProtectedRoute";
const SenderAccounts = lazy(() => import("../features/sender-accounts/pages/SenderAccounts"));
const CreateSenderAccount = lazy(() => import("../features/sender-accounts/pages/CreateSenderAccount"));
const EditSenderAccount = lazy(() => import("../features/sender-accounts/pages/EditSenderAccount"));
const Contacts = lazy(() => import("../features/contacts/pages/Contacts"));
const CreateContact = lazy(() => import("../features/contacts/pages/CreateContact"));
const ContactDetails = lazy(() => import("../features/contacts/pages/ContactDetails"));
const EditContact = lazy(() => import("../features/contacts/pages/EditContact"));
const ContactLists = lazy(() => import("../features/contact-lists/pages/ContactLists"));
const CreateContactList = lazy(() => import("../features/contact-lists/pages/CreateContactList"));
const ManageContactList = lazy(() => import("../features/contact-lists/pages/ManageContactList"));
const Offers = lazy(() => import("../features/offers/pages/Offers"));



function App(){

const scopedPage = (name, page) => (
    <div className={`ui-page-scope ui-page-scope--${name}`}>
        {page}
    </div>
);

return (

<BrowserRouter>

<Suspense fallback={<div className="route-loading" role="status">Loading page…</div>}>
<Routes>


<Route
path="/"
element={scopedPage("auth-login", <Login />)}
/>


<Route
path="/register"
element={scopedPage("auth-register", <Register />)}
/>


<Route
path="/forgot-password"
element={scopedPage("auth-recovery", <ForgotPassword />)}
/>

<Route path="/reset-password" element={scopedPage("auth-recovery", <ResetPassword />)} />


<Route
element={
    <ProtectedRoute>
        <Layout />
    </ProtectedRoute>
}
>

<Route
path="/profile"
element={scopedPage("profile", <Profile />)}
/>

<Route
path="/settings"
element={scopedPage("settings", <SettingsPage />)}
/>

<Route
path="/dashboard"
element={scopedPage("dashboard", <Dashboard />)}
/>


<Route
path="/campaigns"
element={scopedPage("campaign-list", <Campaigns />)}
/>

<Route
path="/campaigns/create"
element={scopedPage("campaign-editor", <CreateCampaign />)}
/>

<Route
path="/campaigns/:id/analytics"
element={scopedPage("campaign-analytics", <Analytics />)}
/>

<Route
path="/campaigns/:id/performance"
element={scopedPage("campaign-performance", <CampaignPerformance />)}
/>

<Route
path="/campaigns/:id/details"
element={scopedPage("campaign-details", <CampaignDetails />)}
/>


<Route
path="/campaigns/:id/edit"
element={scopedPage("campaign-editor", <EditCampaign />)}
/>

<Route path="/templates" element={scopedPage("templates", <Templates />)} />
<Route path="/templates/create" element={scopedPage("template-editor", <CreateTemplate />)} />
<Route path="/templates/:id/edit" element={scopedPage("template-editor", <EditTemplate />)} />
<Route path="/offers" element={scopedPage("offers", <Offers />)} />

<Route path="/emails" element={scopedPage("email-generation", <Emails />)} />
<Route path="/emails/create" element={scopedPage("email-generation", <CreateEmail />)} />
<Route path="/emails/:id" element={scopedPage("email-generation", <EmailDetails />)} />


<Route path="/senders" element={scopedPage("sender-accounts", <SenderAccounts />)} />
<Route path="/senders/create" element={scopedPage("sender-editor", <CreateSenderAccount />)} />
<Route path="/senders/:id/edit" element={scopedPage("sender-editor", <EditSenderAccount />)} />

<Route path="/contacts" element={scopedPage("contacts", <Contacts />)} />
<Route path="/contacts/create" element={scopedPage("contact-editor", <CreateContact />)} />
<Route path="/contacts/:id/edit" element={scopedPage("contact-editor", <EditContact />)} />
<Route path="/contacts/:id" element={scopedPage("contact-details", <ContactDetails />)} />
<Route path="/contact-lists/:id/manage" element={scopedPage("contact-lists", <ManageContactList />)} />


<Route path="/contact-lists" element={scopedPage("contact-lists", <ContactLists />)} />
<Route path="/contact-lists/create" element={scopedPage("contact-lists", <CreateContactList />)} />

</Route>

<Route path="*" element={<main className="route-not-found"><h1>Page not found</h1><p>This page doesn’t exist or may have moved.</p><Link to="/dashboard">Back to dashboard</Link></main>} />


</Routes>
</Suspense>

</BrowserRouter>

)

}

export default App;
