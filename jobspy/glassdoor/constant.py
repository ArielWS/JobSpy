import random

# List of possible User-Agent strings for rotation
user_agents = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Firefox/89.0",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Edge/91.0.864.59",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 6.1; WOW64; rv:42.0) Gecko/20100101 Firefox/42.0",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Safari/537.36 Edge/91.0.864.67",
]

# Base headers template for GraphQL and other requests (excluding rotating fields)
base_headers = {
    "authority": "www.glassdoor.com",
    "accept": "*/*",
    "accept-language": "en-US,en;q=0.9",
    "apollographql-client-name": "job-search-next",
    "apollographql-client-version": "4.65.5",
    "content-type": "application/json",
    "origin": "https://www.glassdoor.com",
    "referer": "https://www.glassdoor.com/",
    # The following 'sec-ch-ua' fields can conflict with rotating UA, so omitted.
    #"sec-ch-ua": '"Chromium";v="118", "Google Chrome";v="118", "Not=A?Brand";v="99"',
    #"sec-ch-ua-mobile": "?0",
    #"sec-ch-ua-platform": '"macOS"',
    "sec-fetch-dest": "empty",
    "sec-fetch-mode": "cors",
    "sec-fetch-site": "same-origin",
}

# Function to get headers with a random User-Agent and static base fields

def get_random_headers(csrf_token: str | None = None) -> dict[str, str]:
    """
    Return a headers dict for Glassdoor requests, merging base_headers,
    a randomly selected User-Agent, and an optional gd-csrf-token.
    """
    headers = base_headers.copy()
    headers["user-agent"] = random.choice(user_agents)
    if csrf_token:
        headers["gd-csrf-token"] = csrf_token
    return headers

# GraphQL query template
query_template = """
        query JobSearchResultsQuery(
            $excludeJobListingIds: [Long!], 
            $keyword: String, 
            $locationId: Int, 
            $locationType: LocationTypeEnum, 
            $numJobsToShow: Int!, 
            $pageCursor: String, 
            $pageNumber: Int, 
            $filterParams: [FilterParams], 
            $originalPageUrl: String, 
            $seoFriendlyUrlInput: String, 
            $parameterUrlInput: String, 
            $seoUrl: Boolean
        ) {
            jobListings(
                contextHolder: {
                    searchParams: {
                        excludeJobListingIds: $excludeJobListingIds, 
                        keyword: $keyword, 
                        locationId: $locationId, 
                        locationType: $locationType, 
                        numPerPage: $numJobsToShow, 
                        pageCursor: $pageCursor, 
                        pageNumber: $pageNumber, 
                        filterParams: $filterParams, 
                        originalPageUrl: $originalPageUrl, 
                        seoFriendlyUrlInput: $seoFriendlyUrlInput, 
                        parameterUrlInput: $parameterUrlInput, 
                        seoUrl: $seoUrl, 
                        searchType: SR
                    }
                }
            ) {
                companyFilterOptions {
                    id
                    shortName
                    __typename
                }
                filterOptions
                indeedCtk
                jobListings {
                    ...JobView
                    __typename
                }
                jobListingSeoLinks {
                    linkItems {
                        position
                        url
                        __typename
                    }
                    __typename
                }
                jobSearchTrackingKey
                jobsPageSeoData {
                    pageMetaDescription
                    pageTitle
                    __typename
                }
                paginationCursors {
                    cursor
                    pageNumber
                    __typename
                }
                indexablePageForSeo
                searchResultsMetadata {
                    searchCriteria {
                        implicitLocation {
                            id
                            localizedDisplayName
                            type
                            __typename
                        }
                        keyword
                        location {
                            id
                            shortName
                            localizedShortName
                            localizedDisplayName
                            type
                            __typename
                        }
                        __typename
                    }
                    helpCenterDomain
                    helpCenterLocale
                    jobSerpJobOutlook {
                        occupation
                        paragraph
                        __typename
                    }
                    showMachineReadableJobs
                    __typename
                }
                totalJobsCount
                __typename
            }
        }

        fragment JobView on JobListingSearchResult {
            jobview {
                header {
                    adOrderId
                    advertiserType
                    adOrderSponsorshipLevel
                    ageInDays
                    divisionEmployerName
                    easyApply
                    employer {
                        id
                        name
                        shortName
                        __typename
                    }
                    employerNameFromSearch
                    goc
                    gocConfidence
                    gocId
                    jobCountryId
                    jobLink
                    jobResultTrackingKey
                    jobTitleText
                    locationName
                    locationType
                    locId
                    needsCommission
                    payCurrency
                    payPeriod
                    payPeriodAdjustedPay {
                        p10
                        p50
                        p90
                        __typename
                    }
                    rating
                    salarySource
                    savedJobId
                    sponsored
                    __typename
                }
                job {
                    description
                    importConfigId
                    jobTitleId
                    jobTitleText
                    listingId
                    __typename
                }
                jobListingAdminDetails {
                    cpcVal
                    importConfigId
                    jobListingId
                    jobSourceId
                    userEligibleForAdminJobDetails
                    __typename
                }
                overview {
                    shortName
                    squareLogoUrl
                    __typename
                }
                __typename
            }
            __typename
        }
"""

# Fallback token if CSRF cannot be retrieved
fallback_token = "Ft6oHEWlRZrxDww95Cpazw:0pGUrkb2y3TyOpAIqF2vbPmUXoXVkD3oEGDVkvfeCerceQ5-n8mBg3BovySUIjmCPHCaW0H2nQVdqzbtsYqf4Q:wcqRqeegRUa9MVLJGyujVXB7vWFPjdaS1CtrrzJq-ok"
