import "./LoginFooter.css";

export default function LoginFooter(){

    return(

        <footer className="login-footer">

            <div className="footer-brand">✉ AI Email Marketing</div>


            <div className="footer-copy">

                © {new Date().getFullYear()} AI Email Marketing.

            </div>

        </footer>

    );

}
