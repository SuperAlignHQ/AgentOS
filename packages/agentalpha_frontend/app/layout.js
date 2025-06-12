import "./globals.css"

export const metadata = {
  title: "SuperAlign",
  description: "HSBC Project for the OCR Service",
 
};

export default function RootLayout({ children }) {
  return (
    <html lang="en">
      <body>
      <link rel="icon" href="/Hsbc.svg" />
        {children}
      </body>
    </html>
  );
}
